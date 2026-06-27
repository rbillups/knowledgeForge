import logging
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config.settings import settings
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.models.knowledge_collection import KnowledgeCollection
from app.schemas.document import (
    DocumentDeleteResponse,
    DocumentReindexResponse,
    DocumentResponse,
    DocumentUploadResponse,
)
from app.services.chunk_embedding_service import apply_embeddings_to_chunks
from app.services.chunking import chunk_text, estimate_tokens
from app.services.exceptions import (
    CollectionNotFoundError,
    DocumentDeletionError,
    DocumentNotFoundError,
    DocumentProcessingError,
    EmbeddingGenerationError,
    MissingApiKeyError,
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


def get_collection_by_slug(db: Session, slug: str) -> KnowledgeCollection | None:
    return db.scalar(
        select(KnowledgeCollection).where(KnowledgeCollection.slug == slug)
    )


def find_document_in_collection(
    db: Session,
    *,
    collection_id: int,
    filename: str,
    source_type: str | None = None,
) -> Document | None:
    stmt = select(Document).where(
        Document.collection_id == collection_id,
        Document.filename == filename,
    )
    if source_type is not None:
        stmt = stmt.where(Document.source_type == source_type)

    return db.scalar(stmt)


def import_markdown_file(
    db: Session,
    *,
    collection_id: int,
    source_path: Path,
    source_type: str = "portfolio",
    title: str | None = None,
) -> tuple[Document, str, int]:
    filename = source_path.name
    file_type = resolve_file_type(filename)
    file_bytes = source_path.read_bytes()
    document_title = title or Path(filename).stem

    existing = find_document_in_collection(
        db,
        collection_id=collection_id,
        filename=filename,
        source_type=source_type,
    )

    if existing is not None:
        document = existing
        document.title = document_title
        document.status = "processing"
        document.error_message = None
        db.commit()
        db.refresh(document)

        db.query(DocumentChunk).filter(
            DocumentChunk.document_id == document.id
        ).delete()
        db.commit()

        upload_path = _save_upload_file(document.id, filename, file_bytes)
        _index_document_from_path(db, document, upload_path, file_type)
        return document, "updated", document.chunk_count

    document = Document(
        collection_id=collection_id,
        filename=filename,
        title=document_title,
        file_type=file_type,
        source_type=source_type,
        status="processing",
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    upload_path = _save_upload_file(document.id, filename, file_bytes)

    try:
        _index_document_from_path(db, document, upload_path, file_type)
        return document, "created", document.chunk_count
    except DocumentProcessingError as exc:
        _mark_document_failed(db, document, exc.message)
        raise
    except MissingApiKeyError:
        _mark_document_failed(db, document, MissingApiKeyError.message)
        raise
    except EmbeddingGenerationError as exc:
        _mark_document_failed(db, document, exc.message)
        raise DocumentProcessingError(exc.message) from exc
    except Exception:
        logger.exception(
            "Unexpected failure while importing markdown file %s",
            filename,
        )
        _mark_document_failed(
            db,
            document,
            "An unexpected error occurred while processing the document.",
        )
        raise DocumentProcessingError(
            "An unexpected error occurred while processing the document."
        ) from None


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
        _index_document_from_path(db, document, upload_path, file_type)
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
    except MissingApiKeyError:
        _mark_document_failed(
            db,
            document,
            MissingApiKeyError.message,
        )
        raise
    except EmbeddingGenerationError as exc:
        _mark_document_failed(db, document, exc.message)
        raise DocumentProcessingError(exc.message) from exc
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


def reindex_document(db: Session, document_id: int) -> DocumentReindexResponse:
    document = db.get(Document, document_id)
    if document is None:
        raise DocumentNotFoundError(document_id)

    upload_path = _find_uploaded_file(document.id, document.filename)
    if upload_path is None:
        raise DocumentProcessingError(
            "The original uploaded file could not be found for reindexing."
        )

    document.status = "processing"
    document.error_message = None
    db.commit()

    try:
        db.query(DocumentChunk).filter(
            DocumentChunk.document_id == document.id
        ).delete()
        db.commit()

        _index_document_from_path(
            db,
            document,
            upload_path,
            document.file_type,
        )

        return DocumentReindexResponse(
            id=document.id,
            filename=document.filename,
            title=document.title,
            status=document.status,
            chunk_count=document.chunk_count,
            message="Document reindexed successfully.",
        )
    except DocumentProcessingError as exc:
        _mark_document_failed(db, document, exc.message)
        raise
    except MissingApiKeyError:
        _mark_document_failed(
            db,
            document,
            MissingApiKeyError.message,
        )
        raise
    except EmbeddingGenerationError as exc:
        _mark_document_failed(db, document, exc.message)
        raise DocumentProcessingError(exc.message) from exc
    except Exception:
        logger.exception("Unexpected failure while reindexing document %s", document.id)
        _mark_document_failed(
            db,
            document,
            "An unexpected error occurred while reindexing the document.",
        )
        raise DocumentProcessingError(
            "An unexpected error occurred while reindexing the document."
        ) from None


def delete_document(db: Session, document_id: int) -> DocumentDeleteResponse:
    document = db.get(Document, document_id)
    if document is None:
        raise DocumentNotFoundError(document_id)

    filename = document.filename
    upload_path = _find_uploaded_file(document.id, document.filename)

    try:
        # document_chunks rows cascade via FK on delete; ORM relationship also
        # uses delete-orphan for in-session cleanup.
        db.delete(document)
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("Failed to delete document %s", document_id)
        raise DocumentDeletionError(document_id) from None

    if upload_path is not None:
        _remove_upload_file(upload_path, document_id=document_id)

    logger.info("Deleted document %s", document_id)

    return DocumentDeleteResponse(
        document_id=document_id,
        filename=filename,
        deleted=True,
    )


def _index_document_from_path(
    db: Session,
    document: Document,
    upload_path: Path,
    file_type: str,
) -> None:
    text, page_count = extract_text(upload_path, file_type)
    chunks = chunk_text(text)
    if not chunks:
        raise DocumentProcessingError(
            "No readable text chunks could be created from the document."
        )

    chunk_rows: list[DocumentChunk] = []
    for index, content in enumerate(chunks):
        chunk = DocumentChunk(
            document_id=document.id,
            chunk_index=index,
            content=content,
            token_estimate=estimate_tokens(content),
        )
        db.add(chunk)
        chunk_rows.append(chunk)

    db.flush()

    apply_embeddings_to_chunks(
        db,
        chunk_ids=[chunk.id for chunk in chunk_rows],
        chunk_texts=[chunk.content for chunk in chunk_rows],
    )

    document.status = "indexed"
    document.page_count = page_count
    document.chunk_count = len(chunks)
    document.error_message = None
    db.commit()
    db.refresh(document)

    logger.info(
        "Indexed document %s with %s embedded chunks",
        document.id,
        document.chunk_count,
    )


def _save_upload_file(document_id: int, filename: str, file_bytes: bytes) -> Path:
    document_dir = settings.upload_dir / str(document_id)
    document_dir.mkdir(parents=True, exist_ok=True)
    destination = document_dir / Path(filename).name
    destination.write_bytes(file_bytes)
    return destination


def _find_uploaded_file(document_id: int, filename: str) -> Path | None:
    destination = settings.upload_dir / str(document_id) / Path(filename).name
    if destination.exists():
        return destination
    return None


def _remove_upload_file(upload_path: Path, *, document_id: int) -> None:
    expected_parent = (settings.upload_dir / str(document_id)).resolve()
    resolved_path = upload_path.resolve()

    if expected_parent not in resolved_path.parents:
        logger.warning(
            "Skipped removing upload file outside document directory for %s",
            document_id,
        )
        return

    try:
        resolved_path.unlink(missing_ok=True)
        if expected_parent.exists() and not any(expected_parent.iterdir()):
            expected_parent.rmdir()
    except OSError:
        logger.warning(
            "Could not remove upload file for document %s",
            document_id,
        )


def _mark_document_failed(db: Session, document: Document, message: str) -> None:
    document.status = "failed"
    document.error_message = message
    document.chunk_count = 0
    db.query(DocumentChunk).filter(
        DocumentChunk.document_id == document.id
    ).delete()
    db.commit()
    logger.warning("Document %s failed processing: %s", document.id, message)
