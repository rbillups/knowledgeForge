from collections.abc import Generator
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.config.settings import get_settings
from app.database.session import get_db
from app.middleware.public_portfolio_lockdown import (
    is_public_portfolio_route_allowed,
    public_portfolio_lockdown_response,
)


@pytest.fixture
def mock_db() -> MagicMock:
    return MagicMock()


def _build_client(
    mock_db: MagicMock,
    *,
    public_portfolio_mode: bool,
) -> Generator[TestClient, None, None]:
    get_settings.cache_clear()

    with patch(
        "app.middleware.public_portfolio_lockdown.settings.public_portfolio_mode",
        public_portfolio_mode,
    ), patch(
        "app.main.settings.public_portfolio_mode",
        public_portfolio_mode,
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


@pytest.fixture
def internal_mode_client(mock_db: MagicMock) -> Generator[TestClient, None, None]:
    yield from _build_client(mock_db, public_portfolio_mode=False)


@pytest.fixture
def public_mode_client(mock_db: MagicMock) -> Generator[TestClient, None, None]:
    yield from _build_client(mock_db, public_portfolio_mode=True)


def test_route_allowlist_matches_required_public_endpoints() -> None:
    assert is_public_portfolio_route_allowed("GET", "/health") is True
    assert is_public_portfolio_route_allowed("GET", "/api/v1/health/ready") is True
    assert (
        is_public_portfolio_route_allowed(
            "POST",
            "/api/v1/public/portfolio/chat",
        )
        is True
    )
    assert is_public_portfolio_route_allowed("POST", "/api/v1/chat") is False


def test_lockdown_returns_none_when_public_mode_disabled() -> None:
    assert (
        public_portfolio_lockdown_response(
            public_portfolio_mode=False,
            method="POST",
            path="/api/v1/chat",
        )
        is None
    )


@patch("app.api.routes.public_portfolio.public_portfolio_chat")
def test_public_mode_allows_public_portfolio_chat(
    mock_public_portfolio_chat: MagicMock,
    public_mode_client: TestClient,
) -> None:
    from app.schemas.chat import ChatResponse

    mock_public_portfolio_chat.return_value = ChatResponse(
        answer="Answer",
        citations=[],
        insufficient_context=False,
        policy_blocked=False,
        model="gpt-4.1-mini",
    )

    response = public_mode_client.post(
        "/api/v1/public/portfolio/chat",
        json={"question": "What is KnowledgeForge?"},
    )

    assert response.status_code == 200


@patch("app.api.routes.chat.grounded_chat")
def test_public_mode_blocks_internal_chat(
    mock_grounded_chat: MagicMock,
    public_mode_client: TestClient,
) -> None:
    response = public_mode_client.post(
        "/api/v1/chat",
        json={
            "collection_id": 1,
            "question": "What is KnowledgeForge?",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Not found."
    mock_grounded_chat.assert_not_called()


def test_public_mode_blocks_document_routes(public_mode_client: TestClient) -> None:
    list_response = public_mode_client.get("/api/v1/documents")
    upload_response = public_mode_client.post(
        "/api/v1/documents/upload",
        data={"collection_id": "1"},
        files={"file": ("notes.txt", b"hello", "text/plain")},
    )
    delete_response = public_mode_client.delete("/api/v1/documents/1")

    assert list_response.status_code == 404
    assert upload_response.status_code == 404
    assert delete_response.status_code == 404


def test_public_mode_blocks_dashboard_and_feedback(
    public_mode_client: TestClient,
) -> None:
    dashboard_response = public_mode_client.get("/api/v1/dashboard/summary")
    feedback_response = public_mode_client.get("/api/v1/feedback/summary")
    submit_response = public_mode_client.post(
        "/api/v1/feedback",
        json={
            "collection_id": 1,
            "question": "Q",
            "answer": "A",
            "feedback_type": "helpful",
        },
    )

    assert dashboard_response.status_code == 404
    assert feedback_response.status_code == 404
    assert submit_response.status_code == 404


def test_public_mode_blocks_docs_and_openapi(public_mode_client: TestClient) -> None:
    docs_response = public_mode_client.get("/docs")
    redoc_response = public_mode_client.get("/redoc")
    openapi_response = public_mode_client.get("/openapi.json")

    assert docs_response.status_code == 404
    assert redoc_response.status_code == 404
    assert openapi_response.status_code == 404


def test_public_mode_allows_health_and_readiness(public_mode_client: TestClient) -> None:
    health_response = public_mode_client.get("/health")
    ready_response = public_mode_client.get("/api/v1/health/ready")

    assert health_response.status_code == 200
    assert ready_response.status_code in {200, 503}


@patch("app.api.routes.chat.grounded_chat")
def test_internal_mode_preserves_internal_chat(
    mock_grounded_chat: MagicMock,
    internal_mode_client: TestClient,
) -> None:
    from app.schemas.chat import ChatResponse
    from app.services.rate_limit_service import chat_rate_limiter

    chat_rate_limiter.reset()

    mock_grounded_chat.return_value = ChatResponse(
        answer="Internal answer",
        citations=[],
        insufficient_context=False,
        policy_blocked=False,
        model="gpt-4.1-mini",
    )

    response = internal_mode_client.post(
        "/api/v1/chat",
        json={
            "collection_id": 1,
            "question": "What is KnowledgeForge?",
        },
    )

    assert response.status_code == 200


def test_internal_mode_preserves_document_listing(
    internal_mode_client: TestClient,
    mock_db: MagicMock,
) -> None:
    with patch("app.api.routes.documents.list_documents", return_value=[]):
        response = internal_mode_client.get("/api/v1/documents")

    assert response.status_code == 200


def test_internal_mode_exposes_openapi_docs(internal_mode_client: TestClient) -> None:
    response = internal_mode_client.get("/openapi.json")

    assert response.status_code == 200
