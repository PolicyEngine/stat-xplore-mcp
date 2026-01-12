"""Modal deployment for Stat-Xplore API."""

from pathlib import Path

import modal

app = modal.App("stat-xplore-api")

# Get the directory containing this file
package_dir = Path(__file__).parent

image = modal.Image.debian_slim(python_version="3.11").pip_install(
    "fastapi>=0.115.0",
    "httpx>=0.28.0",
    "pydantic>=2.10.0",
    "pydantic-settings>=2.7.0",
    "python-dotenv>=1.0.1",
    "uvicorn>=0.34.0",
)


@app.function(
    image=image,
    secrets=[modal.Secret.from_name("stat-xplore")],
    keep_warm=1,
    mounts=[modal.Mount.from_local_dir(package_dir, remote_path="/root/stat_xplore_mcp")],
)
@modal.asgi_app()
def fastapi_app():
    """Deploy the FastAPI app to Modal."""
    import os
    import sys

    # Add the source directory to path
    sys.path.insert(0, "/root")

    # Set environment variable from Modal secret
    os.environ["STAT_XPLORE_API_KEY"] = os.environ.get("STAT_XPLORE_API_KEY", "")

    from stat_xplore_mcp.api import app as api_app

    return api_app


@app.local_entrypoint()
def main():
    """Local entrypoint for testing."""
    print("Deploying Stat-Xplore API to Modal...")
    print("Run 'modal deploy src/stat_xplore_mcp/modal_app.py' to deploy")
