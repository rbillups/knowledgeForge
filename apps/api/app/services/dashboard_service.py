import logging

from sqlalchemy import case, func, select, text
from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.knowledge_collection import KnowledgeCollection
from app.schemas.dashboard import (
    DashboardCollectionSummary,
    DashboardRecentDocument,
    DashboardSummaryResponse,
)

logger = logging.getLogger(__name__)

PROCESSING_STATUSES = ("uploaded", "processing")


def check_database_status(db: Session) -> str:
    try:
        db.execute(text("SELECT 1"))
        return "ok"
    except Exception:
        logger.exception("Database health check failed")
        return "unavailable"


def get_dashboard_summary(db: Session) -> DashboardSummaryResponse:
    database_status = check_database_status(db)

    total_collections = db.scalar(select(func.count()).select_from(KnowledgeCollection)) or 0
    total_documents = db.scalar(select(func.count()).select_from(Document)) or 0
    total_indexed_documents = (
        db.scalar(
            select(func.count())
            .select_from(Document)
            .where(Document.status == "indexed")
        )
        or 0
    )
    total_processing_documents = (
        db.scalar(
            select(func.count())
            .select_from(Document)
            .where(Document.status.in_(PROCESSING_STATUSES))
        )
        or 0
    )
    total_failed_documents = (
        db.scalar(
            select(func.count())
            .select_from(Document)
            .where(Document.status == "failed")
        )
        or 0
    )
    total_chunks = (
        db.scalar(select(func.coalesce(func.sum(Document.chunk_count), 0)))
        or 0
    )

    recent_rows = db.execute(
        select(
            Document.title,
            Document.filename,
            Document.status,
            Document.chunk_count,
            Document.updated_at,
            KnowledgeCollection.name.label("collection_name"),
        )
        .join(
            KnowledgeCollection,
            Document.collection_id == KnowledgeCollection.id,
        )
        .order_by(Document.updated_at.desc(), Document.created_at.desc())
        .limit(5)
    ).all()

    collection_rows = db.execute(
        select(
            KnowledgeCollection.id,
            KnowledgeCollection.slug,
            KnowledgeCollection.name,
            func.count(Document.id).label("document_count"),
            func.coalesce(
                func.sum(case((Document.status == "indexed", 1), else_=0)),
                0,
            ).label("indexed_document_count"),
            func.coalesce(func.sum(Document.chunk_count), 0).label("chunk_count"),
        )
        .outerjoin(Document, Document.collection_id == KnowledgeCollection.id)
        .group_by(
            KnowledgeCollection.id,
            KnowledgeCollection.slug,
            KnowledgeCollection.name,
        )
        .order_by(KnowledgeCollection.name.asc())
    ).all()

    return DashboardSummaryResponse(
        total_collections=total_collections,
        total_documents=total_documents,
        total_indexed_documents=total_indexed_documents,
        total_processing_documents=total_processing_documents,
        total_failed_documents=total_failed_documents,
        total_chunks=total_chunks,
        recent_documents=[
            DashboardRecentDocument(
                title=title,
                filename=filename,
                collection_name=collection_name,
                status=status,
                chunk_count=chunk_count,
                updated_at=updated_at,
            )
            for title, filename, status, chunk_count, updated_at, collection_name in recent_rows
        ],
        collections=[
            DashboardCollectionSummary(
                id=collection_id,
                slug=slug,
                name=name,
                document_count=document_count,
                indexed_document_count=int(indexed_document_count),
                chunk_count=int(chunk_count),
            )
            for collection_id, slug, name, document_count, indexed_document_count, chunk_count in collection_rows
        ],
        api_status="ok",
        database_status=database_status,
    )
