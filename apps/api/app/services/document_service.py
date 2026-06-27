import logging
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

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
from app.services.storage import (
    build_document_storage_key,
    content_type_for_file_type,
    get_storage_backend,
)

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

        upload_key = _save_upload_file(document.id, filename, file_bytes, file_type)
        _index_document(db, document, upload_key, file_type)
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

    upload_key = _save_upload_file(document.id, filename, file_bytes, file_type)

    try:
        _index_document(db, document, upload_key, file_type)
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

    upload_key = _save_upload_file(document.id, filename, file_bytes, file_type)

    try:
        _index_document(db, document, upload_key, file_type)
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

    storage_key = build_document_storage_key(document.id, document.filename)
    storage = get_storage_backend()
    if not storage.exists(storage_key):
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

        _index_document(
            db,
            document,
            storage_key,
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
    storage_key = build_document_storage_key(document.id, document.filename)

    try:
        # document_chunks rows cascade via FK on delete; ORM relationship also
        # uses delete-orphan for in-session cleanup.
        db.delete(document)
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("Failed to delete document %s", document_id)
        raise DocumentDeletionError(document_id) from None

    storage = get_storage_backend()
    if storage.exists(storage_key):
        storage.delete(storage_key)

    logger.info("Deleted document %s", document_id)

    return DocumentDeleteResponse(
        document_id=document_id,
        filename=filename,
        deleted=True,
    )


def _index_document(
    db: Session,
    document: Document,
    storage_key: str,
    file_type: str,
) -> None:
    storage = get_storage_backend()
    with storage.materialize(storage_key) as file_path:
        text, page_count = extract_text(file_path, file_type)

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


def _save_upload_file(
    document_id: int,
    filename: str,
    file_bytes: bytes,
    file_type: str,
) -> str:
    storage = get_storage_backend()
    storage_key = build_document_storage_key(document_id, filename)
    storage.save(
        storage_key,
        file_bytes,
        content_type=content_type_for_file_type(file_type),
    )
    return storage_key


def _mark_document_failed(db: Session, document: Document, message: str) -> None:
    document.status = "failed"
    document.error_message = message
    document.chunk_count = 0
    db.query(DocumentChunk).filter(
        DocumentChunk.document_id == document.id
    ).delete()
    db.commit()
    logger.warning("Document %s failed processing: %s", document.id, message)
