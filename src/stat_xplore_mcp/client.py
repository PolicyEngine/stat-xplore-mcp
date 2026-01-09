"""Stat-Xplore API client."""

import httpx
from rich.console import Console

from stat_xplore_mcp.config import settings
from stat_xplore_mcp.models import (
    RateLimitInfo,
    SchemaItem,
    TableQuery,
    TableQueryResponse,
)

console = Console()


class StatXploreClient:
    """Client for the Stat-Xplore Open Data API."""

    def __init__(self, api_key: str | None = None, base_url: str | None = None):
        self.api_key = api_key or settings.stat_xplore_api_key
        self.base_url = base_url or settings.stat_xplore_base_url
        self._client = httpx.Client(
            base_url=self.base_url,
            headers={"APIKey": self.api_key},
            timeout=120.0,
        )

    def _get_rate_limit_from_headers(
        self, headers: httpx.Headers
    ) -> RateLimitInfo | None:
        """Extract rate limit info from response headers."""
        try:
            return RateLimitInfo(
                limit=int(headers.get("X-RateLimit", 2000)),
                remaining=int(headers.get("X-RateLimit-Remaining", 0)),
                reset_timestamp=int(headers.get("X-RateLimit-Reset", 0)),
            )
        except (ValueError, TypeError):
            return None

    def get_schema(self, schema_id: str | None = None) -> SchemaItem:
        """Get schema information.

        Args:
            schema_id: Optional schema ID to retrieve. If None, returns root.

        Returns:
            Schema item with children.
        """
        url = "/schema" if not schema_id else f"/schema/{schema_id}"
        response = self._client.get(url)
        response.raise_for_status()
        return SchemaItem.model_validate(response.json())

    def list_databases(self) -> list[SchemaItem]:
        """List all available databases (recursively finds all DATABASE items)."""
        databases: list[SchemaItem] = []

        def find_databases(item: SchemaItem, depth: int = 0) -> None:
            if item.type == "DATABASE":
                databases.append(item)
                return
            # For folders, fetch their children if not already loaded
            if item.type == "FOLDER" and not item.children and item.id:
                try:
                    fetched = self.get_schema(item.id)
                    item.children = fetched.children
                except Exception:
                    pass
            if item.children:
                for child in item.children:
                    find_databases(child, depth + 1)

        root = self.get_schema()
        find_databases(root)
        return databases

    def get_database_info(self, database_id: str) -> SchemaItem:
        """Get detailed info about a specific database.

        Args:
            database_id: The database ID (e.g., 'str:database:PIP_Monthly')

        Returns:
            Database schema information including fields and measures.
        """
        # Extract just the ID part after 'str:database:'
        if database_id.startswith("str:database:"):
            schema_path = database_id
        else:
            schema_path = f"str:database:{database_id}"
        return self.get_schema(schema_path)

    def query_table(self, query: TableQuery) -> TableQueryResponse:
        """Execute a table query.

        Args:
            query: The table query specification.

        Returns:
            Query results with fields, measures, and data cubes.
        """
        response = self._client.post(
            "/table",
            json=query.model_dump(exclude_none=True),
            headers={"Content-Type": "application/json"},
        )
        response.raise_for_status()
        return TableQueryResponse.model_validate(response.json())

    def query_table_simple(
        self,
        database: str,
        measures: list[str],
        row_fields: list[str],
        column_fields: list[str] | None = None,
        filters: dict[str, list[str]] | None = None,
    ) -> TableQueryResponse:
        """Execute a simplified table query.

        Args:
            database: Database ID
            measures: List of measure IDs to retrieve
            row_fields: Fields for row dimension
            column_fields: Optional fields for column dimension
            filters: Optional dict mapping field IDs to lists of value IDs to include

        Returns:
            Query results.
        """
        dimensions = [row_fields]
        if column_fields:
            dimensions.append(column_fields)

        recodes = None
        if filters:
            recodes = {
                field_id: {"map": [[v] for v in values]}
                for field_id, values in filters.items()
            }

        query = TableQuery(
            database=database,
            measures=measures,
            dimensions=dimensions,
            recodes=recodes,
        )
        return self.query_table(query)

    def get_rate_limit(self) -> RateLimitInfo:
        """Get current rate limit status."""
        response = self._client.get("/rate_limit")
        response.raise_for_status()
        data = response.json()
        return RateLimitInfo(
            limit=data.get("limit", 2000),
            remaining=data.get("remaining", 0),
            reset_timestamp=data.get("reset", 0),
        )

    def get_info(self) -> dict:
        """Get API instance information."""
        response = self._client.get("/info")
        response.raise_for_status()
        return response.json()

    def close(self) -> None:
        """Close the HTTP client."""
        self._client.close()

    def __enter__(self) -> "StatXploreClient":
        return self

    def __exit__(self, *args) -> None:
        self.close()
