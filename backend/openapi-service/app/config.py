from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "RPA OpenAPI"
    API_VERSION: str = "1.0"
    DATABASE_URL: str
    DATABASE_USERNAME: str
    DATABASE_PASSWORD: str
    REDIS_URL: str

    LOG_LEVEL: str = "INFO"
    LOG_DIR: str = "/var/log/rpa-openapi"

    # URL credentials are disabled by default because query strings commonly
    # appear in browser history and proxy access logs.
    MCP_ALLOW_QUERY_API_KEY: bool = False

    model_config = SettingsConfigDict(
        env_file=None,
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
