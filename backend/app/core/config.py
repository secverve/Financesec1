from functools import lru_cache
from typing import List, Union

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "MTS FDS Platform"
    app_env: str = "local"
    api_v1_prefix: str = "/api/v1"
    secret_key: str = "change-me"
    access_token_expire_minutes: int = 120
    database_url: str = "postgresql+psycopg://mts:mts@localhost:5432/mts"
    redis_url: str = "redis://localhost:6379/0"
    market_data_provider: str = "mock"
    default_admin_email: str = "admin@example.com"
    default_admin_password: str = "Admin1234!"
    default_user_email: str = "user@example.com"
    default_user_password: str = "User1234!"
    additional_auth_code: str = "000000"
    cors_origins: Union[List[str], str] = ["http://localhost:3000"]

    model_config = SettingsConfigDict(env_file=".env.example", case_sensitive=False)

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value):
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
