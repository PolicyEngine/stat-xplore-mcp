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
- `query_table` - query statistics data with full support for dimensions, recodes, and statistical functions
- `browse_schema` - navigate the schema hierarchy
- `get_rate_limit` - check API rate limit status

## Query Examples

### Basic count query

```json
{
  "database": "str:database:HBAI",
  "measures": ["str:count:HBAI:V_F_HBAI"],
  "dimensions": [["str:field:HBAI:V_F_HBAI:YEAR"]]
}
```

### Median income query

For median/mean calculations, use statistical function measures with the pattern:
`str:statfn:{database}:{view}:{measure}:{MEDIAN|MEAN}`

```json
{
  "database": "str:database:HBAI",
  "measures": [
    "str:statfn:HBAI:V_F_HBAI:S_OE_BHC:MEDIAN",
    "str:statfn:HBAI:V_F_HBAI:S_OE_AHC:MEDIAN"
  ],
  "dimensions": [
    ["str:field:HBAI:V_F_HBAI:YEAR"],
    ["str:field:HBAI:V_F_HBAI:KIDECOBU_WORK"]
  ],
  "recodes": {
    "str:field:HBAI:V_F_HBAI:YEAR": {
      "map": [
        ["str:value:HBAI:V_F_HBAI:YEAR:C_HBAI_YEAR:2223"],
        ["str:value:HBAI:V_F_HBAI:YEAR:C_HBAI_YEAR:2324"]
      ]
    },
    "str:field:HBAI:V_F_HBAI:KIDECOBU_WORK": {
      "map": [
        ["str:value:HBAI:V_F_HBAI:KIDECOBU_WORK:C_HBAI_KIDECOBU_WORK:1"]
      ]
    }
  }
}
```

### Recodes structure

Recodes filter and group values:
- `map`: List of value groups. Each inner array becomes one row/column. Multiple values in same array are combined.
- `total`: Set to `true` to include a total row/column.

```json
{
  "str:field:HBAI:V_F_HBAI:NEWFAMBU": {
    "map": [
      ["str:value:...:1"],
      ["str:value:...:2", "str:value:...:3"]
    ],
    "total": true
  }
}
```
