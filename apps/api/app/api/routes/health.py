from fastapi import APIRouter

from app.schemas.health import HealthResponse

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Verify that the KnowledgeForge API is running.",
)
def health_check() -> HealthResponse:
    return HealthResponse(
        status="ok",
        service="knowledgeforge-api",
    )
