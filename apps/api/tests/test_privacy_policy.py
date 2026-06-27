from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.orm import Session

from app.schemas.chat import ChatRequest
from app.services.chat_service import grounded_chat
from app.services.privacy_policy_service import (
    PRIVACY_BLOCKED_ANSWER,
    is_privacy_sensitive_question,
)


@pytest.mark.parametrize(
    "question",
    [
        "What is Key'Shawn Billups' personal phone number and home address?",
        "What is Key'Shawn's home address?",
        "What is his personal phone number?",
        "Where does he live exactly?",
    ],
)
def test_privacy_policy_blocks_sensitive_contact_requests(question: str) -> None:
    assert is_privacy_sensitive_question(question) is True


def test_privacy_policy_allows_public_contact_request() -> None:
    assert (
        is_privacy_sensitive_question(
            "How can I contact Key'Shawn professionally?"
        )
        is False
    )


@patch("app.services.chat_service.semantic_search")
@patch("app.services.chat_service.generate_grounded_answer")
def test_blocked_request_skips_retrieval_and_openai(
    mock_generate_answer: MagicMock,
    mock_semantic_search: MagicMock,
) -> None:
    db = MagicMock(spec=Session)
    response = grounded_chat(
        db,
        ChatRequest(
            collection_id=1,
            question="What is his personal phone number?",
            retrieval_limit=5,
        ),
    )

    assert response.policy_blocked is True
    assert response.insufficient_context is True
    assert response.citations == []
    assert response.model is None
    assert response.answer == PRIVACY_BLOCKED_ANSWER
    mock_semantic_search.assert_not_called()
    mock_generate_answer.assert_not_called()


@patch("app.services.chat_service.is_privacy_sensitive_question", return_value=False)
@patch("app.services.chat_service.semantic_search")
@patch("app.services.chat_service.generate_grounded_answer")
def test_public_contact_request_uses_normal_chat_flow(
    mock_generate_answer: MagicMock,
    mock_semantic_search: MagicMock,
    _mock_privacy_check: MagicMock,
) -> None:
    from app.schemas.search import SearchResponse, SearchResultItem

    mock_semantic_search.return_value = SearchResponse(
        collection_id=1,
        query="How can I contact Key'Shawn professionally?",
        limit=5,
        results=[
            SearchResultItem(
                document_title="Contact",
                filename="07_contact.md",
                chunk_content="Use rkbillups.com",
                chunk_index=0,
                page_number=None,
                similarity_score=0.9,
            )
        ],
    )
    mock_generate_answer.return_value = (
        "Use Key'Shawn's portfolio contact page at rkbillups.com."
    )

    db = MagicMock(spec=Session)
    response = grounded_chat(
        db,
        ChatRequest(
            collection_id=1,
            question="How can I contact Key'Shawn professionally?",
            retrieval_limit=5,
        ),
    )

    assert response.policy_blocked is False
    assert response.insufficient_context is False
    mock_semantic_search.assert_called_once()
    mock_generate_answer.assert_called_once()
