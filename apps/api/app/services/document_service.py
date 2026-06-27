import logging
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config.settings import settings
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.models.knowledge_collection import KnowledgeCollection
from app.schemas.document import DocumentResponse, DocumentUploadResponse
from app.services.chunking import chunk_text, estimate_tokens
from app.services.exceptions import (
    CollectionNotFoundError,
    DocumentProcessingError,
    UnsupportedFileTypeError,
)
from app.services.text_extraction import extract_text

logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {
    ".pdf": "pdf",
    ".txt": "txt",
    ".md": "markdown",
    ".markdown": "markdown",
}


def list_collections(db: Session) -> list[KnowledgeCollection]:
    return db.scalars(
        select(KnowledgeCollection).order_by(KnowledgeCollection.name.asc())
    ).all()


def list_documents(db: Session) -> list[DocumentResponse]:
    rows = db.execute(
        select(
            Document,
            KnowledgeCollection.name.label("collection_name"),
        )
        .join(
            KnowledgeCollection,
            Document.collection_id == KnowledgeCollection.id,
        )
        .order_by(Document.created_at.desc())
    ).all()

    return [
        DocumentResponse(
            id=document.id,
            collection_id=document.collection_id,
            collection_name=collection_name,
            filename=document.filename,
            title=document.title,
            file_type=document.file_type,
            source_type=document.source_type,
            status=document.status,
            page_count=document.page_count,
            chunk_count=document.chunk_count,
            error_message=document.error_message,
            created_at=document.created_at,
            updated_at=document.updated_at,
        )
        for document, collection_name in rows
    ]


def resolve_file_type(filename: str) -> str:
    extension = Path(filename).suffix.lower()
    file_type = ALLOWED_EXTENSIONS.get(extension)
    if file_type is None:
        raise UnsupportedFileTypeError(filename)
    return file_type


def upload_document(
    db: Session,
    *,
    filename: str,
    file_bytes: bytes,
    collection_id: int,
) -> DocumentUploadResponse:
    file_type = resolve_file_type(filename)
    collection = db.get(KnowledgeCollection, collection_id)
    if collection is None:
        raise CollectionNotFoundError(collection_id)

    title = Path(filename).stem
    document = Document(
        collection_id=collection_id,
        filename=filename,
        title=title,
        file_type=file_type,
        source_type="upload",
        status="processing",
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    upload_path = _save_upload_file(document.id, filename, file_bytes)

    try:
        text, page_count = extract_text(upload_path, file_type)
        chunks = chunk_text(text)
        if not chunks:
            raise DocumentProcessingError(
                "No readable text chunks could be created from the document."
            )

        for index, chunk in enumerate(chunks):
            db.add(
                DocumentChunk(
                    document_id=document.id,
                    chunk_index=index,
                    content=chunk,
                    token_estimate=estimate_tokens(chunk),
                )
            )

        document.status = "indexed"
        document.page_count = page_count
        document.chunk_count = len(chunks)
        document.error_message = None
        db.commit()
        db.refresh(document)

        logger.info(
            "Indexed document %s with %s chunks",
            document.id,
            document.chunk_count,
        )

        return DocumentUploadResponse(
            id=document.id,
            filename=document.filename,
            title=document.title,
            file_type=document.file_type,
            status=document.status,
            chunk_count=document.chunk_count,
            page_count=document.page_count,
            message="Document uploaded and indexed successfully.",
        )
    except DocumentProcessingError as exc:
        _mark_document_failed(db, document, exc.message)
        raise
    except Exception:
        logger.exception("Unexpected failure while processing document %s", document.id)
        _mark_document_failed(
            db,
            document,
            "An unexpected error occurred while processing the document.",
        )
        raise DocumentProcessingError(
            "An unexpected error occurred while processing the document."
        ) from None


def _save_upload_file(document_id: int, filename: str, file_bytes: bytes) -> Path:
    document_dir = settings.upload_dir / str(document_id)
    document_dir.mkdir(parents=True, exist_ok=True)
    destination = document_dir / Path(filename).name
    destination.write_bytes(file_bytes)
    return destination


def _mark_document_failed(db: Session, document: Document, message: str) -> None:
    document.status = "failed"
    document.error_message = message
    document.chunk_count = 0
    db.query(DocumentChunk).filter(
        DocumentChunk.document_id == document.id
    ).delete()
    db.commit()
    logger.warning("Document %s failed processing: %s", document.id, message)
