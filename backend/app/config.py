"""Application configuration using Pydantic BaseSettings.

You can override values with a `.env` file placed next to `main.py` or by setting
environment variables with the same names.
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from pathlib import Path

class Settings(BaseSettings):
    # Project root (directory containing this file)
    PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent

    # SQLite database – stored inside the project for easy dev setup
    DATABASE_URL: str = Field(default_factory=lambda: f"sqlite:///{Settings().PROJECT_ROOT / 'app.db'}")

    # Allowed origins for CORS – adjust when deploying behind a domain
    ALLOWED_ORIGINS: list[str] = ["*"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Export a singleton for import elsewhere
settings = Settings()

