# Stat-Xplore MCP

MCP server for querying DWP Stat-Xplore benefit statistics.

## Claude Code setup

```bash
claude mcp add stat-xplore -e STAT_XPLORE_API_KEY=your_key -- uvx --from git+https://github.com/PolicyEngine/stat-xplore-mcp stat-xplore-mcp
```

Get an API key from [Stat-Xplore](https://stat-xplore.dwp.gov.uk) under Account > Open Data API Access.

## Tools

- `list_databases` - list all 118 benefit datasets (UC, PIP, ESA, etc.)
- `get_database_schema` - get fields and measures for a database
- `query_table` - query statistics data
- `browse_schema` - navigate the schema hierarchy
- `get_rate_limit` - check API rate limit status
