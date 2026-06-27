import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.search import SearchRequest, SearchResponse
from app.services.exceptions import (
    CollectionNotFoundError,
    EmbeddingGenerationError,
    MissingApiKeyError,
)
from app.services.search_service import semantic_search

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/search", tags=["Search"])


@router.post(
    "",
    response_model=SearchResponse,
    summary="Search indexed knowledge",
    description=(
        "Generate an embedding for the query and return the most relevant "
        "document chunks from the selected collection using pgvector cosine similarity."
    ),
)
def search_endpoint(
    request: SearchRequest,
    db: Session = Depends(get_db),
) -> SearchResponse:
    try:
        return semantic_search(db, request)
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
        logger.error("Embedding generation failed for semantic search request")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=exc.message,
        ) from exc
