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
    """Save API key to config file."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump({"api_key": api_key}, f)


def prompt_for_api_key() -> str:
    """Prompt user for API key via stderr (MCP servers use stdout for protocol)."""
    sys.stderr.write(
        "\n╔══════════════════════════════════════════════════════════════════╗\n"
        "║           Stat-Xplore MCP - API Key Required                     ║\n"
        "╠══════════════════════════════════════════════════════════════════╣\n"
        "║ Get your API key from: https://stat-xplore.dwp.gov.uk            ║\n"
        "║ Go to: Account > Open Data API Access                            ║\n"
        "╚══════════════════════════════════════════════════════════════════╝\n\n"
    )
    sys.stderr.write("Enter your Stat-Xplore API key: ")
    sys.stderr.flush()

    api_key = input().strip()

    if api_key:
        save_api_key(api_key)
        sys.stderr.write(f"API key saved to {CONFIG_FILE}\n")
        sys.stderr.flush()

    return api_key


def get_api_key() -> str:
    """Get API key from environment, config file, or prompt user."""
    # First check environment variable
    settings = Settings()
    if settings.stat_xplore_api_key:
        return settings.stat_xplore_api_key

    # Then check config file
    stored_key = load_stored_api_key()
    if stored_key:
        return stored_key

    # Finally prompt user
    return prompt_for_api_key()


class Settings(BaseSettings):
    """Application settings loaded from environment."""

    stat_xplore_api_key: str = ""
    stat_xplore_base_url: str = "https://stat-xplore.dwp.gov.uk/webapi/rest/v1"


settings = Settings()
