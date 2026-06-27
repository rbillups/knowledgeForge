from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException, Request
from fastapi.testclient import TestClient

from app.services.rate_limit_service import InMemoryRateLimiter


def _build_request(client_host: str = "127.0.0.1") -> Request:
    scope = {
        "type": "http",
        "method": "POST",
        "path": "/api/v1/chat",
        "headers": [],
        "client": (client_host, 12345),
    }
    return Request(scope)


def test_rate_limiter_blocks_after_max_requests() -> None:
    limiter = InMemoryRateLimiter(max_requests=2, window_seconds=600)
    request = _build_request()

    limiter.check(request)
    limiter.check(request)

    with pytest.raises(HTTPException) as exc_info:
        limiter.check(request)

    assert exc_info.value.status_code == 429


def test_rate_limiter_reset_clears_state() -> None:
    limiter = InMemoryRateLimiter(max_requests=1, window_seconds=600)
    request = _build_request()

    limiter.check(request)
    limiter.reset()
    limiter.check(request)


@patch("app.api.routes.chat.grounded_chat")
def test_chat_endpoint_returns_429_when_rate_limited(
    mock_grounded_chat: MagicMock,
    client: TestClient,
) -> None:
    from app.schemas.chat import ChatResponse
    from app.services.rate_limit_service import chat_rate_limiter

    chat_rate_limiter.reset()
    original_max = chat_rate_limiter.max_requests
    chat_rate_limiter.max_requests = 1

    mock_grounded_chat.return_value = ChatResponse(
        answer="Answer",
        citations=[],
        insufficient_context=False,
        policy_blocked=False,
        model="gpt-4.1-mini",
    )

    payload = {
        "collection_id": 1,
        "question": "What is KnowledgeForge?",
    }

    first = client.post("/api/v1/chat", json=payload)
    second = client.post("/api/v1/chat", json=payload)

    chat_rate_limiter.max_requests = original_max
    chat_rate_limiter.reset()

    assert first.status_code == 200
    assert second.status_code == 429
    assert "Too many chat requests" in second.json()["detail"]
