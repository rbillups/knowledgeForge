import logging

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config.settings import settings
from app.schemas.health import ReadinessResponse
from app.services.storage.factory import get_storage_backend

logger = logging.getLogger(__name__)


def check_database_status(db: Session) -> str:
    try:
        db.execute(text("SELECT 1"))
        return "ok"
    except Exception:
        logger.exception("Database readiness check failed")
        return "unavailable"


def check_storage_status() -> str:
    try:
        storage = get_storage_backend()
        return "ok" if storage.check_availability() else "unavailable"
    except Exception:
        logger.exception("Storage readiness check failed")
        return "unavailable"


def get_readiness(db: Session) -> ReadinessResponse:
    database_status = check_database_status(db)
    storage_status = check_storage_status()
    ready = database_status == "ok" and storage_status == "ok"

    return ReadinessResponse(
        ready=ready,
        environment=settings.app_env,
        storage_provider=settings.storage_provider,
        database_status=database_status,
        storage_status=storage_status,
    )
