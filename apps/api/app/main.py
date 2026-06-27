import logging
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import (
    chat,
    collections,
    dashboard,
    documents,
    feedback,
    health,
    public_portfolio,
    search,
)
from app.config.settings import get_settings
from app.middleware.public_portfolio_lockdown import PublicPortfolioLockdownMiddleware
from app.services.storage.factory import get_storage_backend

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    app_settings = get_settings()

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        if app_settings.public_portfolio_mode:
            logger.info("Public portfolio mode enabled")
        else:
            logger.info("Internal development mode enabled")

        if app_settings.storage_provider == "local":
            app_settings.upload_dir.mkdir(parents=True, exist_ok=True)
            logger.info("Local upload directory ready")
        else:
            logger.info("Using Supabase Storage provider")

        storage = get_storage_backend()
        if storage.check_availability():
            logger.info("Storage availability check passed")
        else:
            logger.warning("Storage availability check failed during startup")

        yield

    docs_url = None if app_settings.public_portfolio_mode else "/docs"
    redoc_url = None if app_settings.public_portfolio_mode else "/redoc"
    openapi_url = None if app_settings.public_portfolio_mode else "/openapi.json"

    app = FastAPI(
        title="KnowledgeForge API",
        description=(
            "Citation-grounded AI knowledge assistant API for document "
            "upload, indexing, and retrieval."
        ),
        version="0.1.0",
        lifespan=lifespan,
        docs_url=docs_url,
        redoc_url=redoc_url,
        openapi_url=openapi_url,
        openapi_tags=[
            {
                "name": "Health",
                "description": "Service health and readiness checks.",
            },
            {
                "name": "Collections",
                "description": "Knowledge collection management endpoints.",
            },
            {
                "name": "Documents",
                "description": "Document upload, listing, reindexing, and deletion endpoints.",
            },
            {
                "name": "Dashboard",
                "description": "Operational dashboard metrics and summaries.",
            },
            {
                "name": "Search",
                "description": "Semantic retrieval over indexed document chunks.",
            },
            {
                "name": "Chat",
                "description": "Grounded question answering over retrieved source chunks.",
            },
            {
                "name": "Feedback",
                "description": "Anonymous answer feedback and operational summaries.",
            },
            {
                "name": "Public Portfolio",
                "description": "Public portfolio assistant scoped to the portfolio collection.",
            },
        ],
    )

    app.add_middleware(PublicPortfolioLockdownMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=app_settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        logger.exception("Unhandled error on %s", request.url.path)
        return JSONResponse(
            status_code=500,
            content={"detail": "An internal server error occurred."},
        )

    app.include_router(health.router)
    app.include_router(health.v1_router, prefix="/api/v1")
    app.include_router(collections.router, prefix="/api/v1")
    app.include_router(dashboard.router, prefix="/api/v1")
    app.include_router(documents.router, prefix="/api/v1")
    app.include_router(search.router, prefix="/api/v1")
    app.include_router(chat.router, prefix="/api/v1")
    app.include_router(public_portfolio.router, prefix="/api/v1")
    app.include_router(feedback.router, prefix="/api/v1")

    return app


app = create_app()
