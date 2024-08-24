from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    project_name: str = Field("Users", alias="PROJECT_NAME")
    postgres_user: str = Field("app", alias="POSTGRES_USER")
    postgres_db: str = Field("database", alias="POSTGRES_DB")
    postgres_password: str = Field("postgres", alias="users_postgres")
    postgres_host: str = Field("postgres", alias="POSTGRES_HOST")
    postgres_port: int = Field(5432, alias="POSTGRES_PORT")
    redis_host: str = Field("127.0.0.1", alias="REDIS_HOST")
    redis_port: int = Field(6379, alias="REDIS_PORT")


settings = Settings()
