from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables and .env file.
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", env_prefix="BGU_")

    log_level: str = Field(
        default="INFO", 
        description="Logging level (DEBUG, INFO, WARNING, ERROR)"
    )
    service_interval_seconds: float = Field(
        default=5.0, 
        ge=0.1, 
        description="Example service tick interval"
    )
    environment: str = Field(
        default="development", 
        description="Environment name"
    )

    # Example of optional settings
    sentry_dsn: str | None = Field(default=None, description="Sentry DSN for error reporting")


def load_settings() -> Settings:
    return Settings()


__all__ = ["Settings", "load_settings"]