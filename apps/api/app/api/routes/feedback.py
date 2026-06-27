import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.feedback import (
    FeedbackCreateRequest,
    FeedbackCreateResponse,
    FeedbackSummaryResponse,
)
from app.services.exceptions import CollectionNotFoundError
from app.services.feedback_service import create_feedback, get_feedback_summary

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/feedback", tags=["Feedback"])


@router.post(
    "",
    response_model=FeedbackCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit answer feedback",
    description=(
        "Record anonymous helpful or not helpful feedback for a grounded "
        "assistant answer. No user identity or personal data is stored."
    ),
)
def submit_feedback_endpoint(
    request: FeedbackCreateRequest,
    db: Session = Depends(get_db),
) -> FeedbackCreateResponse:
    try:
        return create_feedback(db, request)
    except CollectionNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=exc.message,
        ) from exc
    except SQLAlchemyError:
        logger.exception("Failed to store feedback")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to record feedback at this time.",
        ) from None


@router.get(
    "/summary",
    response_model=FeedbackSummaryResponse,
    summary="Feedback summary",
    description=(
        "Return operational feedback totals and recent anonymous ratings."
    ),
)
def get_feedback_summary_endpoint(
    db: Session = Depends(get_db),
) -> FeedbackSummaryResponse:
    try:
        return get_feedback_summary(db)
    except SQLAlchemyError:
        logger.exception("Failed to load feedback summary")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to load feedback summary at this time.",
        ) from None
