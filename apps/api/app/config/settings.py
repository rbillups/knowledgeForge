import json
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

API_ROOT = Path(__file__).resolve().parents[2]


def parse_cors_allowed_origins(value: object) -> list[str]:
    if value is None:
        return []

    if isinstance(value, list):
        candidates = [str(item).strip() for item in value]
    elif isinstance(value, str):
        raw = value.strip()
        if not raw:
            return []

        if raw.startswith("["):
            parsed = json.loads(raw)
            if not isinstance(parsed, list):
                raise ValueError("CORS_ALLOWED_ORIGINS JSON value must be an array.")
            candidates = [str(item).strip() for item in parsed]
        else:
            if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in {'"', "'"}:
                raw = raw[1:-1].strip()
            candidates = [part.strip() for part in raw.split(",")]
    else:
        raise TypeError("CORS_ALLOWED_ORIGINS must be a comma-separated string or JSON array.")

    origins = [origin for origin in candidates if origin]
    if any("," in origin for origin in origins):
        raise ValueError("Each CORS origin must be a single origin without commas.")

    return origins


class Settings(BaseSettings):
    app_env: Literal["development", "production"] = "development"
    storage_provider: Literal["local", "supabase"] = "local"
    public_portfolio_mode: bool = False

    database_url: str
    openai_api_key: str | None = None
    embedding_model: str = "text-embedding-3-small"
    chat_model: str = "gpt-4.1-mini"

    upload_dir: Path = API_ROOT / "uploads"

    supabase_url: str | None = None
    supabase_service_role_key: str | None = None
    supabase_storage_bucket: str | None = None

    cors_allowed_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:3000"],
        description="Frontend origins allowed by CORS.",
    )

    chat_rate_limit_max_requests: int = Field(default=20, ge=1)
    chat_rate_limit_window_seconds: int = Field(default=600, ge=1)

    model_config = SettingsConfigDict(
        env_file=API_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def sqlalchemy_database_url(self) -> str:
        if self.database_url.startswith("postgresql://"):
            return self.database_url.replace(
                "postgresql://",
                "postgresql+psycopg://",
                1,
            )
        if self.database_url.startswith("postgres://"):
            return self.database_url.replace(
                "postgres://",
                "postgresql+psycopg://",
                1,
            )
        return self.database_url

    @property
    def supabase_storage_configured(self) -> bool:
        return bool(
            self.supabase_url
            and self.supabase_service_role_key
            and self.supabase_storage_bucket
        )

    @property
    def cors_origins(self) -> list[str]:
        return self.cors_allowed_origins

    @field_validator("cors_allowed_origins", mode="before")
    @classmethod
    def normalize_cors_allowed_origins(cls, value: object) -> list[str]:
        return parse_cors_allowed_origins(value)

    @model_validator(mode="after")
    def validate_environment(self) -> "Settings":
        if self.storage_provider == "supabase" and not self.supabase_storage_configured:
            raise ValueError(
                "SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, and "
                "SUPABASE_STORAGE_BUCKET are required when STORAGE_PROVIDER=supabase."
            )

        origins = self.cors_origins
        if self.app_env == "production":
            if not origins:
                raise ValueError(
                    "CORS_ALLOWED_ORIGINS must list explicit frontend origins in production."
                )
            if any(origin == "*" for origin in origins):
                raise ValueError("Wildcard CORS origins are not allowed in production.")

        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
