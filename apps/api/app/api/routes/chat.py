import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import grounded_chat
from app.services.exceptions import (
    ChatGenerationError,
    CollectionNotFoundError,
    EmbeddingGenerationError,
    MissingApiKeyError,
)
from app.services.rate_limit_service import enforce_chat_rate_limit

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post(
    "",
    response_model=ChatResponse,
    summary="Ask a grounded question",
    description=(
        "Retrieve the most relevant chunks from the selected collection and "
        "generate a concise answer grounded only in those sources. "
        "Privacy-sensitive requests are blocked before retrieval."
    ),
)
def chat_endpoint(
    request: ChatRequest,
    db: Session = Depends(get_db),
    _: None = Depends(enforce_chat_rate_limit),
) -> ChatResponse:
    try:
        return grounded_chat(db, request)
    except CollectionNotFoundError as exc:
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
        logger.error("Embedding generation failed for chat request")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=exc.message,
        ) from exc
    except ChatGenerationError as exc:
        logger.error("Chat generation failed for collection %s", request.collection_id)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=exc.message,
        ) from exc
