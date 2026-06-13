import json
from typing import Annotated, Any

from pydantic import BeforeValidator, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def parse_cors(v: Any) -> list[str]:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    if isinstance(v, list):
        return [str(item) for item in v]
    if isinstance(v, str):
        parsed = json.loads(v)
        if isinstance(parsed, list):
            return [str(item) for item in parsed]
    raise ValueError(v)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_ignore_empty=True, extra="ignore"
    )

    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "FastAPI Standard"
    ENVIRONMENT: str = "development"

    # CORS settings
    BACKEND_CORS_ORIGINS: Annotated[list[str], BeforeValidator(parse_cors)] = [
        "http://localhost:5173",
        "http://localhost:3000",
    ]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: str | list[str]) -> list[str] | str:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        return v

    # Database settings
    # Default is a local SQLite database using aiosqlite driver
    DATABASE_URL: str = "libsql://[your-database].turso.io"
    TURSO_AUTH_TOKEN: str = ""

    # Rate Limiting
    RATE_LIMIT_DEFAULT: str = "60 per minute"

    # Security settings
    SECRET_KEY: str = "super-secret-temporary-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days


settings = Settings()
