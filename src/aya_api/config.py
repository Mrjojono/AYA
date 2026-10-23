"""Configuration for the AYA API."""

from functools import lru_cache
from typing import ClassVar

from pydantic import PostgresDsn, RedisDsn, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration read from environment variables."""

    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_file=".env", env_prefix="AYA_"
    )

    environment: str = "development"
    database_url: PostgresDsn = PostgresDsn(
        "postgresql+asyncpg://aya:aya@localhost:5432/aya"
    )
    redis_url: RedisDsn = RedisDsn("redis://localhost:6379/0")
    jwt_secret: SecretStr = SecretStr("dev-only-insecure-secret-change-me")
    access_token_ttl_seconds: int = 900
    refresh_token_ttl_seconds: int = 604800


@lru_cache
def get_settings() -> Settings:
    """Return the process-wide validated application configuration."""
    return Settings()
