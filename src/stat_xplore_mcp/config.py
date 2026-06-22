"""Configuration settings."""

import json
import sys
from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Load .env from project root
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)

# Config file location
CONFIG_DIR = Path.home() / ".config" / "stat-xplore-mcp"
CONFIG_FILE = CONFIG_DIR / "config.json"


class MissingAPIKeyError(RuntimeError):
    """Raised when no Stat-Xplore API key can be found."""


SETUP_INSTRUCTIONS = (
    "No Stat-Xplore API key found.\n\n"
    "Get a key from https://stat-xplore.dwp.gov.uk "
    "(Account > Open Data API Access), then provide it in one of two ways:\n\n"
    "  1. Run once in a terminal to save it:\n"
    "       uvx --from git+https://github.com/PolicyEngine/stat-xplore-mcp "
    "stat-xplore-mcp configure\n\n"
    "  2. Or set the STAT_XPLORE_API_KEY environment variable in your MCP "
    "server config.\n\n"
    f"Saved keys live in {CONFIG_FILE}."
)


def load_stored_api_key() -> str | None:
    """Load API key from config file if it exists."""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE) as f:
                config = json.load(f)
                return config.get("api_key")
        except (json.JSONDecodeError, OSError):
            return None
    return None


def save_api_key(api_key: str) -> None:
    """Save API key to config file with owner-only permissions."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump({"api_key": api_key}, f)
    CONFIG_FILE.chmod(0o600)


def configure() -> int:
    """Interactively prompt for an API key and save it.

    Intended to be run from a real terminal (not the MCP stdio server, where
    stdin carries the JSON-RPC protocol). Returns a process exit code.
    """
    sys.stderr.write(
        "Stat-Xplore MCP - API key setup\n"
        "Get your key from https://stat-xplore.dwp.gov.uk "
        "(Account > Open Data API Access)\n\n"
    )

    if not sys.stdin.isatty():
        sys.stderr.write(
            "Error: 'configure' must be run in an interactive terminal.\n"
            "Alternatively set the STAT_XPLORE_API_KEY environment variable.\n"
        )
        return 1

    api_key = input("Enter your Stat-Xplore API key: ").strip()
    if not api_key:
        sys.stderr.write("No key entered. Nothing saved.\n")
        return 1

    save_api_key(api_key)
    sys.stderr.write(f"\nAPI key saved to {CONFIG_FILE}\n")
    return 0


def get_api_key() -> str:
    """Get API key from environment or config file.

    Raises:
        MissingAPIKeyError: if no key is configured, with setup instructions.
    """
    # First check environment variable
    settings = Settings()
    if settings.stat_xplore_api_key:
        return settings.stat_xplore_api_key

    # Then check config file
    stored_key = load_stored_api_key()
    if stored_key:
        return stored_key

    raise MissingAPIKeyError(SETUP_INSTRUCTIONS)


class Settings(BaseSettings):
    """Application settings loaded from environment."""

    stat_xplore_api_key: str = ""
    stat_xplore_base_url: str = "https://stat-xplore.dwp.gov.uk/webapi/rest/v1"


settings = Settings()
