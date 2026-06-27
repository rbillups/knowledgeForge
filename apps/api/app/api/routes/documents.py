import logging

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.document import (
    DocumentReindexResponse,
    DocumentResponse,
    DocumentUploadResponse,
)
from app.services.document_service import list_documents, reindex_document, upload_document
from app.services.exceptions import (
    CollectionNotFoundError,
    DocumentNotFoundError,
    DocumentProcessingError,
    EmbeddingGenerationError,
    MissingApiKeyError,
    UnsupportedFileTypeError,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.get(
    "",
    response_model=list[DocumentResponse],
    summary="List documents",
    description=(
        "Return uploaded documents with collection names and indexing metadata."
    ),
)
def get_documents(db: Session = Depends(get_db)) -> list[DocumentResponse]:
    return list_documents(db)


@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload and index a document",
    description=(
        "Upload a PDF, TXT, or Markdown file. The file is stored locally, "
        "text is extracted, chunked, embedded, and persisted for semantic search."
    ),
)
async def upload_document_endpoint(
    collection_id: int = Form(
        ...,
        description="Knowledge collection that should receive the document.",
    ),
    file: UploadFile = File(..., description="Document file to upload."),
    db: Session = Depends(get_db),
) -> DocumentUploadResponse:
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A filename is required for uploaded files.",
        )

    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded files cannot be empty.",
        )

    try:
        return upload_document(
            db,
            filename=file.filename,
            file_bytes=file_bytes,
            collection_id=collection_id,
        )
    except UnsupportedFileTypeError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=exc.message,
        ) from exc
    except CollectionNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=exc.message,
        ) from exc
    except MissingApiKeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=exc.message,
        ) from exc
    except DocumentProcessingError as exc:
        logger.error("Document processing failed for %s: %s", file.filename, exc.message)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=exc.message,
        ) from exc
    except EmbeddingGenerationError as exc:
        logger.error("Embedding generation failed for %s", file.filename)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=exc.message,
        ) from exc


@router.post(
    "/{document_id}/reindex",
    response_model=DocumentReindexResponse,
    summary="Reindex a document",
    description=(
        "Rebuild chunks and embeddings for an existing uploaded document. "
        "Use this for documents indexed before embeddings were enabled."
    ),
)
def reindex_document_endpoint(
    document_id: int,
    db: Session = Depends(get_db),
) -> DocumentReindexResponse:
    try:
        return reindex_document(db, document_id)
    except DocumentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=exc.message,
        ) from exc
    except MissingApiKeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=exc.message,
        ) from exc
    except DocumentProcessingError as exc:
        logger.error("Document reindex failed for %s: %s", document_id, exc.message)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=exc.message,
        ) from exc
    except EmbeddingGenerationError as exc:
        logger.error("Embedding generation failed during reindex for %s", document_id)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=exc.message,
        ) from exc
