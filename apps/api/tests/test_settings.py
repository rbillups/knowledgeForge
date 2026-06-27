import pytest
from pydantic import ValidationError

from app.config.settings import Settings


def test_development_local_settings_do_not_require_supabase_credentials() -> None:
    settings = Settings(
        database_url="postgresql://test:test@localhost:5432/test",
        app_env="development",
        storage_provider="local",
    )

    assert settings.storage_provider == "local"
    assert settings.supabase_storage_configured is False


def test_supabase_provider_requires_credentials() -> None:
    with pytest.raises(ValidationError, match="SUPABASE_URL"):
        Settings(
            database_url="postgresql://test:test@localhost:5432/test",
            app_env="development",
            storage_provider="supabase",
        )


def test_production_rejects_empty_cors_origins() -> None:
    with pytest.raises(ValidationError, match="CORS_ALLOWED_ORIGINS"):
        Settings(
            database_url="postgresql://test:test@localhost:5432/test",
            app_env="production",
            storage_provider="local",
            cors_allowed_origins="",
        )


def test_production_rejects_wildcard_cors_origins() -> None:
    with pytest.raises(ValidationError, match="Wildcard CORS"):
        Settings(
            database_url="postgresql://test:test@localhost:5432/test",
            app_env="production",
            storage_provider="local",
            cors_allowed_origins="*",
        )


def test_production_accepts_explicit_cors_origins() -> None:
    settings = Settings(
        database_url="postgresql://test:test@localhost:5432/test",
        app_env="production",
        storage_provider="local",
        cors_allowed_origins="https://portfolio.example.com,https://www.example.com",
    )

    assert settings.cors_origins == [
        "https://portfolio.example.com",
        "https://www.example.com",
    ]
