import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.dashboard import DashboardSummaryResponse
from app.services.dashboard_service import get_dashboard_summary

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get(
    "/summary",
    response_model=DashboardSummaryResponse,
    summary="Dashboard summary",
    description=(
        "Return operational metrics for the KnowledgeForge dashboard, including "
        "collection counts, document indexing status, chunk totals, recent "
        "documents, and database connectivity."
    ),
)
def get_dashboard_summary_endpoint(
    db: Session = Depends(get_db),
) -> DashboardSummaryResponse:
    try:
        return get_dashboard_summary(db)
    except SQLAlchemyError:
        logger.exception("Failed to load dashboard summary")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to load dashboard summary at this time.",
        ) from None
