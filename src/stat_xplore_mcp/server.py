"""MCP server for Stat-Xplore API."""

import json

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from stat_xplore_mcp.client import StatXploreClient

server = Server("stat-xplore")


def get_client() -> StatXploreClient:
    """Get a Stat-Xplore client instance."""
    return StatXploreClient()


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available MCP tools."""
    return [
        Tool(
            name="list_databases",
            description="List all available Stat-Xplore databases (benefits datasets)",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="get_database_schema",
            description="Get database schema with available fields and measures",
            inputSchema={
                "type": "object",
                "properties": {
                    "database_id": {
                        "type": "string",
                        "description": "Database ID (e.g., 'str:database:UC_Monthly')",
                    }
                },
                "required": ["database_id"],
            },
        ),
        Tool(
            name="query_table",
            description="Query a Stat-Xplore table to get benefit statistics data",
            inputSchema={
                "type": "object",
                "properties": {
                    "database": {
                        "type": "string",
                        "description": "Database ID (e.g., 'str:database:UC_Monthly')",
                    },
                    "measures": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of measure IDs to retrieve",
                    },
                    "row_fields": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Field IDs for row dimension",
                    },
                    "column_fields": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional field IDs for column dimension",
                    },
                    "filters": {
                        "type": "object",
                        "description": "Filters: field ID -> list of value IDs",
                    },
                },
                "required": ["database", "measures", "row_fields"],
            },
        ),
        Tool(
            name="get_rate_limit",
            description="Check current API rate limit status",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="browse_schema",
            description="Browse the schema hierarchy starting from a path",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Schema path to browse (leave empty for root)",
                    }
                },
                "required": [],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Execute an MCP tool."""
    client = get_client()

    try:
        if name == "list_databases":
            databases = client.list_databases()
            result = [
                {"id": db.id, "label": db.label, "location": db.location}
                for db in databases
            ]
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "get_database_schema":
            schema = client.get_database_info(arguments["database_id"])
            return [
                TextContent(type="text", text=json.dumps(schema.model_dump(), indent=2))
            ]

        elif name == "query_table":
            result = client.query_table_simple(
                database=arguments["database"],
                measures=arguments["measures"],
                row_fields=arguments["row_fields"],
                column_fields=arguments.get("column_fields"),
                filters=arguments.get("filters"),
            )
            return [
                TextContent(type="text", text=json.dumps(result.model_dump(), indent=2))
            ]

        elif name == "get_rate_limit":
            rate_limit = client.get_rate_limit()
            return [
                TextContent(
                    type="text", text=json.dumps(rate_limit.model_dump(), indent=2)
                )
            ]

        elif name == "browse_schema":
            path = arguments.get("path")
            schema = client.get_schema(path)
            return [
                TextContent(type="text", text=json.dumps(schema.model_dump(), indent=2))
            ]

        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

    finally:
        client.close()


def main():
    """Run the MCP server."""
    import asyncio

    async def run():
        async with stdio_server() as (read_stream, write_stream):
            init_options = server.create_initialization_options()
            await server.run(read_stream, write_stream, init_options)

    asyncio.run(run())


if __name__ == "__main__":
    main()
