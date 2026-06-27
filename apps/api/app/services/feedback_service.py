import logging

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.document_feedback import DocumentFeedback
from app.models.knowledge_collection import KnowledgeCollection
from app.schemas.feedback import (
    FeedbackCreateRequest,
    FeedbackCreateResponse,
    FeedbackRecentEntry,
    FeedbackSummaryResponse,
)
from app.services.exceptions import CollectionNotFoundError

logger = logging.getLogger(__name__)

QUESTION_PREVIEW_LENGTH = 100


def resolve_feedback_document_id(
    db: Session,
    *,
    collection_id: int,
    citation_document_ids: list[int] | None,
    citation_filenames: list[str] | None,
) -> int | None:
    if citation_document_ids:
        for document_id in citation_document_ids:
            document = db.scalar(
                select(Document).where(
                    Document.id == document_id,
                    Document.collection_id == collection_id,
                )
            )
            if document is not None:
                return document.id

    if citation_filenames:
        for filename in citation_filenames:
            normalized = filename.strip()
            if not normalized:
                continue
            document = db.scalar(
                select(Document).where(
                    Document.collection_id == collection_id,
                    Document.filename == normalized,
                )
            )
            if document is not None:
                return document.id

    return None


def create_feedback(
    db: Session,
    request: FeedbackCreateRequest,
) -> FeedbackCreateResponse:
    collection = db.get(KnowledgeCollection, request.collection_id)
    if collection is None:
        raise CollectionNotFoundError(request.collection_id)

    document_id = resolve_feedback_document_id(
        db,
        collection_id=request.collection_id,
        citation_document_ids=request.citation_document_ids,
        citation_filenames=request.citation_filenames,
    )

    feedback = DocumentFeedback(
        document_id=document_id,
        question=request.question,
        answer=request.answer,
        rating=request.feedback_type,
        notes=request.comment,
    )
    db.add(feedback)
    db.commit()

    logger.info(
        "Recorded %s feedback for collection %s",
        request.feedback_type,
        request.collection_id,
    )

    return FeedbackCreateResponse(message="Feedback recorded successfully.")


def _question_preview(question: str | None) -> str:
    if not question:
        return "Untitled question"
    stripped = question.strip()
    if len(stripped) <= QUESTION_PREVIEW_LENGTH:
        return stripped
    return f"{stripped[:QUESTION_PREVIEW_LENGTH - 1].rstrip()}…"


def get_feedback_summary(db: Session) -> FeedbackSummaryResponse:
    total_feedback = (
        db.scalar(select(func.count()).select_from(DocumentFeedback)) or 0
    )
    helpful_count = (
        db.scalar(
            select(func.count())
            .select_from(DocumentFeedback)
            .where(DocumentFeedback.rating == "helpful")
        )
        or 0
    )
    not_helpful_count = (
        db.scalar(
            select(func.count())
            .select_from(DocumentFeedback)
            .where(DocumentFeedback.rating == "not_helpful")
        )
        or 0
    )

    helpful_percentage = None
    if total_feedback > 0:
        helpful_percentage = round((helpful_count / total_feedback) * 100, 1)

    recent_rows = db.scalars(
        select(DocumentFeedback)
        .order_by(DocumentFeedback.created_at.desc())
        .limit(5)
    ).all()

    return FeedbackSummaryResponse(
        total_feedback=total_feedback,
        helpful_count=helpful_count,
        not_helpful_count=not_helpful_count,
        helpful_percentage=helpful_percentage,
        recent_feedback=[
            FeedbackRecentEntry(
                question_preview=_question_preview(row.question),
                feedback_type=row.rating,  # type: ignore[arg-type]
                created_at=row.created_at,
            )
            for row in recent_rows
            if row.rating in ("helpful", "not_helpful")
        ],
    )
