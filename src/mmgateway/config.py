from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Read from environment variables prefixed with MMG_ (see .env.example)."""

    model_config = SettingsConfigDict(env_prefix="MMG_", env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://mmgateway:change-me@127.0.0.1:5432/mmgateway"
    debug: bool = False


@lru_cache
def get_settings() -> Settings:
    return Settings()
