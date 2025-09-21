from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    APP_NAME: str = "RPA OpenAPI"
    API_VERSION: str = "1.0"
    DATABASE_URL: str
    DATABASE_USERNAME: str
    DATABASE_PASSWORD: str
    REDIS_URL: str

    LOG_LEVEL: str = "INFO"
    LOG_DIR: str = "/var/log/rpa-openapi"


    model_config = SettingsConfigDict(
        env_file=None,
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache()
def get_settings() -> Settings:
    return Settings()
