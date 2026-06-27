from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.health import HealthResponse, ReadinessResponse
from app.services.readiness_service import get_readiness

router = APIRouter(tags=["Health"])
v1_router = APIRouter(prefix="/health", tags=["Health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Verify that the KnowledgeForge API process is running.",
)
def health_check() -> HealthResponse:
    return HealthResponse(
        status="ok",
        service="knowledgeforge-api",
    )


@v1_router.get(
    "/ready",
    response_model=ReadinessResponse,
    summary="Readiness check",
    description=(
        "Verify database and storage connectivity for deployment readiness. "
        "Does not expose credentials or internal provider details."
    ),
)
def readiness_check(
    db: Session = Depends(get_db),
) -> JSONResponse | ReadinessResponse:
    readiness = get_readiness(db)
    status_code = status.HTTP_200_OK if readiness.ready else status.HTTP_503_SERVICE_UNAVAILABLE
    return JSONResponse(
        status_code=status_code,
        content=readiness.model_dump(),
    )
