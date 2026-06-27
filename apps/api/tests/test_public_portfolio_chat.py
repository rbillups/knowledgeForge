from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from app.schemas.chat import ChatCitation, ChatResponse
from app.schemas.public_portfolio import PublicPortfolioChatRequest
from app.services.exceptions import PortfolioKnowledgeBaseUnavailableError
from app.services.portfolio_public_chat_service import public_portfolio_chat


@patch("app.services.portfolio_public_chat_service.grounded_chat")
@patch("app.services.portfolio_public_chat_service.get_collection_by_slug")
def test_public_portfolio_chat_uses_portfolio_collection(
    mock_get_collection: MagicMock,
    mock_grounded_chat: MagicMock,
) -> None:
    portfolio = MagicMock()
    portfolio.id = 42
    mock_get_collection.return_value = portfolio
    mock_grounded_chat.return_value = ChatResponse(
        answer="KnowledgeForge is a citation-grounded AI platform.",
        citations=[
            ChatCitation(
                document_title="Projects",
                filename="03_projects.md",
                chunk_content="KnowledgeForge supports grounded answers.",
                chunk_index=0,
                page_number=None,
                similarity_score=0.9,
            )
        ],
        insufficient_context=False,
        policy_blocked=False,
        model="gpt-4.1-mini",
    )

    db = MagicMock()
    response = public_portfolio_chat(
        db,
        PublicPortfolioChatRequest(question="What is KnowledgeForge?"),
    )

    mock_get_collection.assert_called_once_with(db, "portfolio")
    mock_grounded_chat.assert_called_once()
    chat_request = mock_grounded_chat.call_args[0][1]
    assert chat_request.collection_id == 42
    assert chat_request.question == "What is KnowledgeForge?"
    assert response.answer.startswith("KnowledgeForge")


def test_public_portfolio_chat_raises_when_portfolio_collection_missing() -> None:
    with patch(
        "app.services.portfolio_public_chat_service.get_collection_by_slug",
        return_value=None,
    ):
        try:
            public_portfolio_chat(
                MagicMock(),
                PublicPortfolioChatRequest(question="What is KnowledgeForge?"),
            )
        except PortfolioKnowledgeBaseUnavailableError as exc:
            assert exc.message == "The portfolio knowledge base is not available."
        else:
            raise AssertionError("Expected PortfolioKnowledgeBaseUnavailableError")


@patch("app.api.routes.public_portfolio.public_portfolio_chat")
def test_public_portfolio_chat_endpoint_rejects_collection_id_in_body(
    mock_public_portfolio_chat: MagicMock,
    client: TestClient,
) -> None:
    mock_public_portfolio_chat.return_value = ChatResponse(
        answer="Answer",
        citations=[],
        insufficient_context=False,
        policy_blocked=False,
        model="gpt-4.1-mini",
    )

    response = client.post(
        "/api/v1/public/portfolio/chat",
        json={
            "question": "What is KnowledgeForge?",
            "collection_id": 999,
        },
    )

    assert response.status_code == 200
    chat_request = mock_public_portfolio_chat.call_args[0][1]
    assert chat_request.question == "What is KnowledgeForge?"
    assert not hasattr(chat_request, "collection_id") or chat_request.collection_id != 999


@patch("app.api.routes.chat.grounded_chat")
def test_internal_chat_endpoint_remains_collection_aware(
    mock_grounded_chat: MagicMock,
    client: TestClient,
) -> None:
    from app.services.rate_limit_service import chat_rate_limiter

    chat_rate_limiter.reset()

    mock_grounded_chat.return_value = ChatResponse(
        answer="Internal answer",
        citations=[],
        insufficient_context=False,
        policy_blocked=False,
        model="gpt-4.1-mini",
    )

    response = client.post(
        "/api/v1/chat",
        json={
            "collection_id": 7,
            "question": "What documents are indexed?",
        },
    )

    assert response.status_code == 200
    chat_request = mock_grounded_chat.call_args[0][1]
    assert chat_request.collection_id == 7


@patch("app.api.routes.public_portfolio.public_portfolio_chat")
def test_public_portfolio_chat_endpoint_returns_not_found_when_unavailable(
    mock_public_portfolio_chat: MagicMock,
    client: TestClient,
) -> None:
    mock_public_portfolio_chat.side_effect = PortfolioKnowledgeBaseUnavailableError()

    response = client.post(
        "/api/v1/public/portfolio/chat",
        json={"question": "What is KnowledgeForge?"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == (
        "The portfolio knowledge base is not available."
    )
