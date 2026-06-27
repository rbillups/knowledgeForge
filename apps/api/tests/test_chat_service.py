from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from app.schemas.search import SearchResponse, SearchResultItem
from app.services.chat_service import INSUFFICIENT_ANSWER


def _sample_search_result() -> SearchResultItem:
    return SearchResultItem(
        document_title="Security Operations Manual",
        filename="security-manual.pdf",
        chunk_content="Production credentials must be rotated every 90 days.",
        chunk_index=0,
        page_number=47,
        similarity_score=0.91,
    )


@patch("app.services.chat_service.generate_grounded_answer")
@patch("app.services.chat_service.semantic_search")
def test_chat_returns_grounded_answer_with_citations(
    mock_semantic_search: MagicMock,
    mock_generate_answer: MagicMock,
    client: TestClient,
) -> None:
    mock_semantic_search.return_value = SearchResponse(
        collection_id=1,
        query="What is our credential rotation policy?",
        limit=5,
        results=[_sample_search_result()],
    )
    mock_generate_answer.return_value = (
        "Production credentials must be rotated every 90 days."
    )

    response = client.post(
        "/api/v1/chat",
        json={
            "collection_id": 1,
            "question": "What is our credential rotation policy?",
            "retrieval_limit": 5,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["insufficient_context"] is False
    assert payload["policy_blocked"] is False
    assert payload["answer"] == (
        "Production credentials must be rotated every 90 days."
    )
    assert payload["model"] == "gpt-4.1-mini"
    assert len(payload["citations"]) == 1
    assert payload["citations"][0]["document_title"] == "Security Operations Manual"
    assert payload["citations"][0]["chunk_content"].startswith("Production credentials")


@patch("app.services.chat_service.generate_grounded_answer")
@patch("app.services.chat_service.semantic_search")
def test_chat_returns_insufficient_context_when_model_cannot_answer(
    mock_semantic_search: MagicMock,
    mock_generate_answer: MagicMock,
    client: TestClient,
) -> None:
    mock_semantic_search.return_value = SearchResponse(
        collection_id=1,
        query="What is our office lunch policy?",
        limit=5,
        results=[_sample_search_result()],
    )
    mock_generate_answer.return_value = INSUFFICIENT_ANSWER

    response = client.post(
        "/api/v1/chat",
        json={
            "collection_id": 1,
            "question": "What is our office lunch policy?",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["insufficient_context"] is True
    assert payload["answer"] == INSUFFICIENT_ANSWER
    assert len(payload["citations"]) == 1


@patch("app.services.chat_service.semantic_search")
def test_chat_returns_insufficient_context_when_no_chunks_found(
    mock_semantic_search: MagicMock,
    client: TestClient,
) -> None:
    mock_semantic_search.return_value = SearchResponse(
        collection_id=1,
        query="What is our credential rotation policy?",
        limit=5,
        results=[],
    )

    response = client.post(
        "/api/v1/chat",
        json={
            "collection_id": 1,
            "question": "What is our credential rotation policy?",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["insufficient_context"] is True
    assert payload["answer"] == INSUFFICIENT_ANSWER
    assert payload["citations"] == []
