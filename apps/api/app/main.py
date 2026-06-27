import logging
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import chat, collections, documents, health, search
from app.config.settings import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        settings.upload_dir.mkdir(parents=True, exist_ok=True)
        logger.info("Upload directory ready at %s", settings.upload_dir)
        yield

    app = FastAPI(
        title="KnowledgeForge API",
        description=(
            "Citation-grounded AI knowledge assistant API for document "
            "upload, indexing, and retrieval."
        ),
        version="0.1.0",
        lifespan=lifespan,
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
                "description": "Document upload, listing, and indexing endpoints.",
            },
            {
                "name": "Search",
                "description": "Semantic retrieval over indexed document chunks.",
            },
            {
                "name": "Chat",
                "description": "Grounded question answering over retrieved source chunks.",
            },
        ],
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
        ],
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
    app.include_router(collections.router, prefix="/api/v1")
    app.include_router(documents.router, prefix="/api/v1")
    app.include_router(search.router, prefix="/api/v1")
    app.include_router(chat.router, prefix="/api/v1")

    return app


app = create_app()
