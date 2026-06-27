import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.chat import ChatResponse
from app.schemas.public_portfolio import PublicPortfolioChatRequest
from app.services.exceptions import (
    ChatGenerationError,
    EmbeddingGenerationError,
    MissingApiKeyError,
    PortfolioKnowledgeBaseUnavailableError,
)
from app.services.portfolio_public_chat_service import public_portfolio_chat
from app.services.rate_limit_service import enforce_chat_rate_limit

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/public/portfolio", tags=["Public Portfolio"])


@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="Ask about public portfolio work",
    description=(
        "Answer questions using only the Portfolio Knowledge Base. "
        "This endpoint is permanently scoped to the public portfolio collection "
        "and does not accept a collection identifier from clients."
    ),
)
def public_portfolio_chat_endpoint(
    request: PublicPortfolioChatRequest,
    db: Session = Depends(get_db),
    _: None = Depends(enforce_chat_rate_limit),
) -> ChatResponse:
    try:
        return public_portfolio_chat(db, request)
    except PortfolioKnowledgeBaseUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=exc.message,
        ) from exc
    except MissingApiKeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=exc.message,
        ) from exc
    except EmbeddingGenerationError as exc:
        logger.error("Embedding generation failed for public portfolio chat request")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=exc.message,
        ) from exc
    except ChatGenerationError as exc:
        logger.error("Public portfolio chat generation failed")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=exc.message,
        ) from exc
