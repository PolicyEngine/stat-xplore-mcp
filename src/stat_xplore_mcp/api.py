"""FastAPI wrapper for Stat-Xplore API."""

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
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


def load_guidance() -> str:
    """Load guidance markdown content."""
    guidance_path = Path(__file__).parent / "guidance.md"
    if guidance_path.exists():
        return guidance_path.read_text()
    return "# Guidance not found\n\nThe guidance.md file could not be loaded."


def markdown_to_html(markdown_content: str) -> str:
    """Convert markdown to simple HTML with styling."""
    # Simple conversion - in production you might use a library like markdown2 or mistune
    html_content = markdown_content.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    lines = html_content.split("\n")
    result = []
    in_code_block = False
    code_lang = ""

    for line in lines:
        if line.startswith("```"):
            if in_code_block:
                result.append("</code></pre>")
                in_code_block = False
                code_lang = ""
            else:
                in_code_block = True
                code_lang = line[3:].strip()
                result.append(f'<pre><code class="language-{code_lang}">')
            continue

        if in_code_block:
            result.append(line)
        elif line.startswith("# "):
            result.append(f"<h1>{line[2:]}</h1>")
        elif line.startswith("## "):
            result.append(f"<h2>{line[3:]}</h2>")
        elif line.startswith("### "):
            result.append(f"<h3>{line[4:]}</h3>")
        elif line.startswith("| "):
            # Simple table row
            cells = [cell.strip() for cell in line.split("|")[1:-1]]
            if all(cell.replace("-", "").strip() == "" for cell in cells):
                # Skip separator rows
                continue
            result.append("<tr>" + "".join(f"<td>{cell}</td>" for cell in cells) + "</tr>")
        elif line.strip().startswith("- "):
            result.append(f"<li>{line.strip()[2:]}</li>")
        elif line.strip() == "":
            result.append("<br>")
        else:
            result.append(f"<p>{line}</p>")

    html = "\n".join(result)

    # Wrap table rows in table tags
    html = html.replace("<tr>", "<table border='1' cellpadding='5' cellspacing='0'><tr>", 1)
    html = html.replace("</tr>\n<br>", "</tr></table>")
    html = html.replace("</tr>\n<p>", "</tr></table>\n<p>")

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Stat-Xplore API Guidance</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                line-height: 1.6;
                max-width: 900px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }}
            h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
            h2 {{ color: #34495e; margin-top: 30px; }}
            h3 {{ color: #7f8c8d; }}
            pre {{
                background-color: #2c3e50;
                color: #ecf0f1;
                padding: 15px;
                border-radius: 5px;
                overflow-x: auto;
            }}
            code {{
                font-family: 'Courier New', Courier, monospace;
                font-size: 0.9em;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
                background-color: white;
            }}
            th, td {{
                padding: 10px;
                text-align: left;
                border: 1px solid #ddd;
            }}
            th {{
                background-color: #3498db;
                color: white;
            }}
            li {{
                margin: 5px 0;
            }}
            .endpoint {{
                background-color: #e8f5e9;
                padding: 10px;
                border-radius: 5px;
                margin: 10px 0;
            }}
        </style>
    </head>
    <body>
        {html}
    </body>
    </html>
    """


@app.get("/")
async def root():
    """API root endpoint with quick links."""
    return {
        "name": "Stat-Xplore API",
        "description": "Access DWP benefit and income statistics via the Stat-Xplore Open Data API",
        "version": "0.1.0",
        "endpoints": {
            "documentation": "/docs",
            "guidance": "/guidance - Comprehensive usage guide and examples",
            "databases": "/databases - List available databases",
            "schema": "/schema - Browse schema hierarchy",
            "rate_limit": "/rate_limit - Check API quota",
        },
        "quick_start": {
            "1": "Visit /guidance for detailed examples and field references",
            "2": "Check /databases to see available datasets (HBAI, UC, PIP, etc.)",
            "3": "Use /table endpoint to query data",
            "4": "See /docs for OpenAPI documentation",
        },
    }


@app.get("/guidance", response_class=HTMLResponse)
async def get_guidance():
    """Get comprehensive API guidance and examples."""
    guidance_content = load_guidance()
    return markdown_to_html(guidance_content)


@app.get("/guidance/raw")
async def get_guidance_raw():
    """Get raw markdown guidance content."""
    return {"content": load_guidance()}


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
