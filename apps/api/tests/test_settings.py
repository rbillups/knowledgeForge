import pytest
from pydantic import ValidationError

from app.config.settings import Settings, parse_cors_allowed_origins


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


def test_parse_cors_allowed_origins_splits_comma_separated_values() -> None:
    origins = parse_cors_allowed_origins(
        "http://localhost:3001, https://rkbillups.com ,https://www.rkbillups.com,",
    )

    assert origins == [
        "http://localhost:3001",
        "https://rkbillups.com",
        "https://www.rkbillups.com",
    ]


def test_parse_cors_allowed_origins_accepts_json_array() -> None:
    origins = parse_cors_allowed_origins(
        '["http://localhost:3001","https://rkbillups.com"]',
    )

    assert origins == ["http://localhost:3001", "https://rkbillups.com"]


def test_parse_cors_allowed_origins_strips_outer_quotes() -> None:
    origins = parse_cors_allowed_origins(
        '"http://localhost:3001,https://rkbillups.com"',
    )

    assert origins == ["http://localhost:3001", "https://rkbillups.com"]


def test_production_rejects_empty_cors_origins() -> None:
    with pytest.raises(ValidationError, match="CORS_ALLOWED_ORIGINS"):
        Settings(
            database_url="postgresql://test:test@localhost:5432/test",
            app_env="production",
            storage_provider="local",
            cors_allowed_origins=[],
        )


def test_production_rejects_wildcard_cors_origins() -> None:
    with pytest.raises(ValidationError, match="Wildcard CORS"):
        Settings(
            database_url="postgresql://test:test@localhost:5432/test",
            app_env="production",
            storage_provider="local",
            cors_allowed_origins=["*"],
        )


def test_production_accepts_explicit_cors_origins() -> None:
    settings = Settings(
        database_url="postgresql://test:test@localhost:5432/test",
        app_env="production",
        storage_provider="local",
        cors_allowed_origins=(
            "https://portfolio.example.com,https://www.example.com"
        ),
    )

    assert settings.cors_origins == [
        "https://portfolio.example.com",
        "https://www.example.com",
    ]
    assert all("," not in origin for origin in settings.cors_origins)


def test_cors_origins_is_a_list_not_one_comma_containing_string() -> None:
    settings = Settings(
        database_url="postgresql://test:test@localhost:5432/test",
        app_env="production",
        storage_provider="local",
        cors_allowed_origins=(
            "http://localhost:3001,https://knowledge-forge-mauve.vercel.app,"
            "https://rkbillups.com,https://www.rkbillups.com"
        ),
    )

    assert len(settings.cors_origins) == 4
    assert settings.cors_origins[0] == "http://localhost:3001"
