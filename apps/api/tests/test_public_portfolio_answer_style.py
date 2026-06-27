from unittest.mock import MagicMock, patch

from app.services.chat_service import grounded_chat
from app.services.portfolio_public_chat_service import (
    PUBLIC_PORTFOLIO_CHAT_SETTINGS,
    public_portfolio_chat,
)
from app.services.public_portfolio_answer_style import (
    PUBLIC_PORTFOLIO_INSUFFICIENT_ANSWER,
    PUBLIC_PORTFOLIO_SYSTEM_INSTRUCTIONS,
    has_markdown_bullets,
    has_markdown_heading,
    is_concise_answer,
    is_simple_factual_answer,
)
from app.schemas.chat import ChatRequest
from app.schemas.public_portfolio import PublicPortfolioChatRequest


EXAMPLE_SKILLS_ANSWER = """\
Key'Shawn is a full-stack software engineer focused on AI systems and product delivery.

- **Backend:** Python, FastAPI, PostgreSQL, and semantic search pipelines
- **Frontend:** TypeScript, React, and Next.js product interfaces
- **AI:** Grounded chat, embeddings, and evaluation-driven assistant design
- **Delivery:** Testing, documentation, and production-minded deployment workflows
"""

EXAMPLE_PROJECT_ANSWER = """\
KnowledgeForge is a citation-grounded AI knowledge assistant for portfolio and document Q&A.

### Highlights
- Uploads and indexes approved source documents
- Retrieves relevant chunks with semantic search
- Generates concise answers with supporting source excerpts
- Includes privacy guardrails for sensitive requests

**Stack:** FastAPI, Next.js, PostgreSQL, pgvector, and OpenAI embeddings.
"""

EXAMPLE_FACTUAL_ANSWER = (
    "KnowledgeForge is a citation-grounded AI knowledge assistant that answers "
    "questions from indexed portfolio documents and shows supporting source excerpts."
)


def test_public_portfolio_prompt_includes_concise_structure_rules() -> None:
    assert "60 and 150 words" in PUBLIC_PORTFOLIO_SYSTEM_INSTRUCTIONS
    assert "Never use tables" in PUBLIC_PORTFOLIO_SYSTEM_INSTRUCTIONS
    assert "Question-type patterns" in PUBLIC_PORTFOLIO_SYSTEM_INSTRUCTIONS
    assert "Skills or strengths" in PUBLIC_PORTFOLIO_SYSTEM_INSTRUCTIONS
    assert "Simple factual questions" in PUBLIC_PORTFOLIO_SYSTEM_INSTRUCTIONS


def test_skills_answer_example_is_concise_and_bulleted() -> None:
    assert has_markdown_bullets(EXAMPLE_SKILLS_ANSWER)
    assert is_concise_answer(EXAMPLE_SKILLS_ANSWER)
    assert "Certainly" not in EXAMPLE_SKILLS_ANSWER


def test_project_answer_example_uses_heading_and_bullets() -> None:
    assert has_markdown_heading(EXAMPLE_PROJECT_ANSWER)
    assert has_markdown_bullets(EXAMPLE_PROJECT_ANSWER)
    assert is_concise_answer(EXAMPLE_PROJECT_ANSWER)


def test_factual_answer_example_stays_simple() -> None:
    assert is_simple_factual_answer(EXAMPLE_FACTUAL_ANSWER)


@patch("app.services.portfolio_public_chat_service.grounded_chat")
@patch("app.services.portfolio_public_chat_service.get_collection_by_slug")
def test_public_portfolio_chat_uses_public_generation_settings(
    mock_get_collection: MagicMock,
    mock_grounded_chat: MagicMock,
) -> None:
    portfolio = MagicMock()
    portfolio.id = 42
    mock_get_collection.return_value = portfolio

    public_portfolio_chat(
        MagicMock(),
        PublicPortfolioChatRequest(question="What are Key'Shawn's skills?"),
    )

    mock_grounded_chat.assert_called_once()
    generation_settings = mock_grounded_chat.call_args.kwargs["generation_settings"]
    assert generation_settings == PUBLIC_PORTFOLIO_CHAT_SETTINGS
    assert (
        generation_settings.system_instructions
        == PUBLIC_PORTFOLIO_SYSTEM_INSTRUCTIONS
    )
    assert (
        generation_settings.insufficient_answer
        == PUBLIC_PORTFOLIO_INSUFFICIENT_ANSWER
    )


@patch("app.services.chat_service.generate_grounded_answer")
@patch("app.services.chat_service.semantic_search")
def test_public_portfolio_grounded_chat_passes_public_instructions_to_model(
    mock_semantic_search: MagicMock,
    mock_generate_answer: MagicMock,
) -> None:
    from app.schemas.search import SearchResponse, SearchResultItem

    mock_semantic_search.return_value = SearchResponse(
        collection_id=1,
        query="What is KnowledgeForge?",
        limit=5,
        results=[
            SearchResultItem(
                document_title="Projects",
                filename="03_projects.md",
                chunk_content="KnowledgeForge is a citation-grounded AI platform.",
                chunk_index=0,
                page_number=None,
                similarity_score=0.9,
            )
        ],
    )
    mock_generate_answer.return_value = EXAMPLE_FACTUAL_ANSWER

    grounded_chat(
        MagicMock(),
        ChatRequest(collection_id=1, question="What is KnowledgeForge?"),
        generation_settings=PUBLIC_PORTFOLIO_CHAT_SETTINGS,
    )

    instructions = mock_generate_answer.call_args.kwargs["system_instructions"]
    assert instructions == PUBLIC_PORTFOLIO_SYSTEM_INSTRUCTIONS


@patch("app.services.chat_service.is_privacy_sensitive_question")
def test_public_portfolio_chat_preserves_privacy_guardrails(
    mock_privacy_check: MagicMock,
) -> None:
    from app.services.privacy_policy_service import PRIVACY_BLOCKED_ANSWER

    mock_privacy_check.return_value = True

    response = grounded_chat(
        MagicMock(),
        ChatRequest(
            collection_id=1,
            question="What is Key'Shawn's home address?",
        ),
        generation_settings=PUBLIC_PORTFOLIO_CHAT_SETTINGS,
    )

    assert response.policy_blocked is True
    assert response.answer == PRIVACY_BLOCKED_ANSWER
    assert response.citations == []


@patch("app.services.chat_service.semantic_search")
def test_public_portfolio_chat_uses_public_insufficient_answer_when_no_sources(
    mock_semantic_search: MagicMock,
) -> None:
    from app.schemas.search import SearchResponse

    mock_semantic_search.return_value = SearchResponse(
        collection_id=1,
        query="What is his salary?",
        limit=5,
        results=[],
    )

    response = grounded_chat(
        MagicMock(),
        ChatRequest(collection_id=1, question="What is his salary?"),
        generation_settings=PUBLIC_PORTFOLIO_CHAT_SETTINGS,
    )

    assert response.insufficient_context is True
    assert response.answer == PUBLIC_PORTFOLIO_INSUFFICIENT_ANSWER
