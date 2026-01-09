"""Configuration settings."""

from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Load .env from project root
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)


class Settings(BaseSettings):
    """Application settings loaded from environment."""

    stat_xplore_api_key: str = ""
    stat_xplore_base_url: str = "https://stat-xplore.dwp.gov.uk/webapi/rest/v1"


settings = Settings()
