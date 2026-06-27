from collections.abc import Generator
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.config.settings import Settings, get_settings
from app.database.session import get_db


@pytest.fixture
def mock_db() -> MagicMock:
    return MagicMock()


@pytest.fixture
def cors_public_mode_client(mock_db: MagicMock) -> Generator[TestClient, None, None]:
    get_settings.cache_clear()

    test_settings = Settings(
        database_url="postgresql://test:test@localhost:5432/test",
        app_env="production",
        storage_provider="local",
        public_portfolio_mode=True,
        cors_allowed_origins=(
            "http://localhost:3001,https://knowledge-forge-mauve.vercel.app,"
            "https://rkbillups.com,https://www.rkbillups.com"
        ),
    )

    with patch("app.main.get_settings", return_value=test_settings), patch(
        "app.middleware.public_portfolio_lockdown.settings",
        test_settings,
    ):
        from app.main import create_app

        app = create_app()

        def override_get_db() -> Generator[MagicMock, None, None]:
            yield mock_db

        app.dependency_overrides[get_db] = override_get_db
        with TestClient(app) as test_client:
            yield test_client
        app.dependency_overrides.clear()

    get_settings.cache_clear()


def test_options_preflight_from_localhost_3001(
    cors_public_mode_client: TestClient,
) -> None:
    response = cors_public_mode_client.options(
        "/api/v1/public/portfolio/chat",
        headers={
            "Origin": "http://localhost:3001",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )

    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:3001"
