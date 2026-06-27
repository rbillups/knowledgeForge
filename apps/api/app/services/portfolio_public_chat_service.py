from sqlalchemy.orm import Session

from app.schemas.chat import ChatRequest, ChatResponse
from app.schemas.public_portfolio import PublicPortfolioChatRequest
from app.services.chat_service import grounded_chat
from app.services.document_service import get_collection_by_slug
from app.services.exceptions import PortfolioKnowledgeBaseUnavailableError
from app.services.public_portfolio_answer_style import (
    PUBLIC_PORTFOLIO_INSUFFICIENT_ANSWER,
    PUBLIC_PORTFOLIO_SYSTEM_INSTRUCTIONS,
    ChatGenerationSettings,
)

PORTFOLIO_COLLECTION_SLUG = "portfolio"

PUBLIC_PORTFOLIO_CHAT_SETTINGS = ChatGenerationSettings(
    system_instructions=PUBLIC_PORTFOLIO_SYSTEM_INSTRUCTIONS,
    insufficient_answer=PUBLIC_PORTFOLIO_INSUFFICIENT_ANSWER,
)


def public_portfolio_chat(
    db: Session,
    request: PublicPortfolioChatRequest,
) -> ChatResponse:
    collection = get_collection_by_slug(db, PORTFOLIO_COLLECTION_SLUG)
    if collection is None:
        raise PortfolioKnowledgeBaseUnavailableError()

    return grounded_chat(
        db,
        ChatRequest(
            collection_id=collection.id,
            question=request.question,
            retrieval_limit=request.retrieval_limit,
        ),
        generation_settings=PUBLIC_PORTFOLIO_CHAT_SETTINGS,
    )
