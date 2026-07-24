from functools import lru_cache
from pathlib import Path
from typing import Annotated

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[2] / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app_name: str = "FoodPlatform API"
    app_env: str = "development"
    app_debug: bool = False
    api_v1_prefix: str = "/api/v1"
    backend_host: str = "127.0.0.1"
    backend_port: int = Field(default=8000, ge=1, le=65535)

    mysql_host: str = "127.0.0.1"
    mysql_port: int = Field(default=3306, ge=1, le=65535)
    mysql_user: str = "food_platform_app"
    mysql_password: SecretStr
    mysql_database: str = "food_platform"
    mysql_charset: str = "utf8mb4"

    neo4j_uri: str = "neo4j://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: SecretStr
    neo4j_database: str = "neo4j"

    cors_origins: Annotated[list[str], NoDecode] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    log_level: str = "INFO"
    jwt_secret: SecretStr
    jwt_algorithm: str = "HS256"
    jwt_access_token_minutes: int = Field(default=60, ge=5, le=1440)

    qwen_enabled: bool = False
    qwen_api_key: SecretStr | None = None
    qwen_model: str = "qwen-plus"
    qwen_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    qwen_timeout_seconds: float = Field(default=8, ge=1, le=60)

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_origins(cls, value: object) -> object:
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    @field_validator("cors_origins")
    @classmethod
    def reject_wildcard(cls, value: list[str]) -> list[str]:
        if "*" in value:
            raise ValueError("CORS_ORIGINS must not contain '*' ")
        return value

    @field_validator("jwt_algorithm")
    @classmethod
    def validate_jwt_algorithm(cls, value: str) -> str:
        if value != "HS256":
            raise ValueError("JWT_ALGORITHM must be HS256")
        return value

    @field_validator("jwt_secret")
    @classmethod
    def validate_jwt_secret(cls, value: SecretStr) -> SecretStr:
        if len(value.get_secret_value()) < 32:
            raise ValueError("JWT_SECRET must contain at least 32 characters")
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
