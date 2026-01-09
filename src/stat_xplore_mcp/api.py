"""FastAPI wrapper for Stat-Xplore API."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from stat_xplore_mcp.client import StatXploreClient
from stat_xplore_mcp.models import (
    RateLimitInfo,
    SchemaItem,
    TableQuery,
    TableQueryResponse,
)

app = FastAPI(
    title="Stat-Xplore API",
    description="API wrapper for DWP Stat-Xplore Open Data API",
    version="0.1.0",
)


class SimpleTableQuery(BaseModel):
    """Simplified table query request."""

    database: str
    measures: list[str]
    row_fields: list[str]
    column_fields: list[str] | None = None
    filters: dict[str, list[str]] | None = None


class DatabaseListItem(BaseModel):
    """Database list item."""

    id: str
    label: str
    location: str


def get_client() -> StatXploreClient:
    """Get a Stat-Xplore client instance."""
    return StatXploreClient()


@app.get("/")
async def root():
    """API root endpoint."""
    return {
        "name": "Stat-Xplore API",
        "version": "0.1.0",
        "docs": "/docs",
    }


@app.get("/databases", response_model=list[DatabaseListItem])
async def list_databases():
    """List all available Stat-Xplore databases."""
    with get_client() as client:
        databases = client.list_databases()
        return [
            DatabaseListItem(id=db.id, label=db.label, location=db.location)
            for db in databases
        ]


@app.get("/schema", response_model=SchemaItem)
async def get_root_schema():
    """Get the root schema."""
    with get_client() as client:
        return client.get_schema()


@app.get("/schema/{schema_id:path}", response_model=SchemaItem)
async def get_schema(schema_id: str):
    """Get schema for a specific path."""
    with get_client() as client:
        try:
            return client.get_schema(schema_id)
        except Exception as e:
            raise HTTPException(status_code=404, detail=str(e))


@app.get("/database/{database_id:path}", response_model=SchemaItem)
async def get_database_info(database_id: str):
    """Get detailed info about a database."""
    with get_client() as client:
        try:
            return client.get_database_info(database_id)
        except Exception as e:
            raise HTTPException(status_code=404, detail=str(e))


@app.post("/table", response_model=TableQueryResponse)
async def query_table(query: TableQuery):
    """Execute a table query."""
    with get_client() as client:
        try:
            return client.query_table(query)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))


@app.post("/table/simple", response_model=TableQueryResponse)
async def query_table_simple(query: SimpleTableQuery):
    """Execute a simplified table query."""
    with get_client() as client:
        try:
            return client.query_table_simple(
                database=query.database,
                measures=query.measures,
                row_fields=query.row_fields,
                column_fields=query.column_fields,
                filters=query.filters,
            )
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))


@app.get("/rate_limit", response_model=RateLimitInfo)
async def get_rate_limit():
    """Get current rate limit status."""
    with get_client() as client:
        return client.get_rate_limit()


@app.get("/info")
async def get_info():
    """Get API instance information."""
    with get_client() as client:
        return client.get_info()
