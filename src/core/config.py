import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_PRODUCTION = "prod"
ENV_LOCAL = "local"
ENV_TEST = "test"


JWT_ALGORITHM = "HS256"

load_dotenv()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")

    ENVIRONMENT: str = ENV_PRODUCTION

    project_name: str = "Auth service"

    postgres_user: str = Field("postgres", alias="POSTGRES_USER")
    postgres_password: str = Field("postgres", alias="POSTGRES_PASSWORD")
    postgres_host: str = Field("db", alias="POSTGRES_HOST")
    postgres_port: int = Field(5432, alias="POSTGRES_PORT")
    postgres_db: str = Field("foo", alias="POSTGRES_DB")
    postgres_url: str = Field(
        "postgresql+asyncpg://postgres:postgres@db:5432/foo", alias="POSTGRES_URL"
    )
    sql_echo: bool = Field(False, alias="SQL_ECHO")

    redis_host: str = Field("127.0.0.1", alias="REDIS_HOST")
    redis_port: int = Field(6379, alias="REDIS_PORT")

    jwt_secret_key: str = Field("my_secret_key", alias="JWT_SECRET_KEY")
    access_token_exp_hours: int = Field(1, alias="ACCESS_TOKEN_EXP_HOURS")
    refresh_token_exp_days: int = Field(10, alias="REFRESH_TOKEN_EXP_DAYS")


@lru_cache
def get_settings() -> Settings:
    environment = os.getenv("ENVIRONMENT", ENV_PRODUCTION)
    root_dir = Path(__file__).parent.parent.parent
    env_file_name = f".env.{environment}"
    if not root_dir.joinpath(env_file_name).exists():
        env_file_name = f".env.{environment}.example"

    env_file_path = root_dir.joinpath(env_file_name)
    return Settings(_env_file=env_file_path, _env_file_encoding="utf-8")


settings = get_settings()
