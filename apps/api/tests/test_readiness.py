from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from app.schemas.health import ReadinessResponse


@patch("app.services.readiness_service.check_storage_status")
@patch("app.services.readiness_service.check_database_status")
def test_readiness_endpoint_returns_ready_when_dependencies_are_ok(
    mock_database_status: MagicMock,
    mock_storage_status: MagicMock,
    client: TestClient,
) -> None:
    mock_database_status.return_value = "ok"
    mock_storage_status.return_value = "ok"

    response = client.get("/api/v1/health/ready")

    assert response.status_code == 200
    payload = response.json()
    assert payload["ready"] is True
    assert payload["database_status"] == "ok"
    assert payload["storage_status"] == "ok"
    assert payload["environment"] in {"development", "production"}
    assert payload["storage_provider"] in {"local", "supabase"}


@patch("app.api.routes.health.get_readiness")
def test_readiness_endpoint_returns_service_unavailable_when_not_ready(
    mock_get_readiness: MagicMock,
    client: TestClient,
) -> None:
    mock_get_readiness.return_value = ReadinessResponse(
        ready=False,
        environment="development",
        storage_provider="local",
        database_status="unavailable",
        storage_status="ok",
    )

    response = client.get("/api/v1/health/ready")

    assert response.status_code == 503
    payload = response.json()
    assert payload["ready"] is False
    assert payload["database_status"] == "unavailable"
