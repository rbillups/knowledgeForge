from sqlalchemy.orm import Session

from app.schemas.chat import ChatRequest, ChatResponse
from app.schemas.public_portfolio import PublicPortfolioChatRequest
from app.services.chat_service import grounded_chat
from app.services.document_service import get_collection_by_slug
from app.services.exceptions import PortfolioKnowledgeBaseUnavailableError

PORTFOLIO_COLLECTION_SLUG = "portfolio"


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
    )
