from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.schemas.document import DocumentDeleteResponse
from app.services.document_service import delete_document
from app.services.exceptions import DocumentDeletionError, DocumentNotFoundError


def _make_document(
    *,
    document_id: int = 1,
    filename: str = "test-notes.md",
) -> Document:
    document = Document(
        collection_id=1,
        filename=filename,
        title="Test Notes",
        file_type="markdown",
        source_type="upload",
        status="indexed",
        chunk_count=2,
    )
    document.id = document_id
    document.chunks = [
        DocumentChunk(
            document_id=document_id,
            chunk_index=0,
            content="chunk one",
        ),
        DocumentChunk(
            document_id=document_id,
            chunk_index=1,
            content="chunk two",
        ),
    ]
    return document


@patch("app.services.document_service.settings")
def test_delete_document_success(
    mock_settings: MagicMock,
    tmp_path: Path,
) -> None:
    mock_settings.upload_dir = tmp_path
    document = _make_document(document_id=5, filename="test-notes.md")
    upload_dir = tmp_path / "5"
    upload_dir.mkdir(parents=True)
    upload_file = upload_dir / "test-notes.md"
    upload_file.write_text("# Test notes", encoding="utf-8")

    db = MagicMock()
    db.get.return_value = document

    response = delete_document(db, 5)

    assert response == DocumentDeleteResponse(
        document_id=5,
        filename="test-notes.md",
        deleted=True,
    )
    db.delete.assert_called_once_with(document)
    db.commit.assert_called_once()
    assert not upload_file.exists()
    assert not upload_dir.exists()


def test_delete_document_raises_for_missing_document() -> None:
    db = MagicMock()
    db.get.return_value = None

    with pytest.raises(DocumentNotFoundError, match="Document 404 was not found"):
        delete_document(db, 404)

    db.delete.assert_not_called()
    db.commit.assert_not_called()


@patch("app.services.document_service.settings")
def test_delete_document_removes_associated_chunks_via_orm_delete(
    mock_settings: MagicMock,
    tmp_path: Path,
) -> None:
    mock_settings.upload_dir = tmp_path
    document = _make_document(document_id=7)
    db = MagicMock()
    db.get.return_value = document

    delete_document(db, 7)

    deleted_document = db.delete.call_args[0][0]
    assert deleted_document.id == 7
    assert len(deleted_document.chunks) == 2


@patch("app.services.document_service.settings")
def test_delete_document_does_not_affect_unrelated_documents(
    mock_settings: MagicMock,
    tmp_path: Path,
) -> None:
    mock_settings.upload_dir = tmp_path
    target = _make_document(document_id=10, filename="remove-me.md")
    db = MagicMock()
    db.get.return_value = target

    delete_document(db, 10)

    db.delete.assert_called_once()
    deleted_document = db.delete.call_args[0][0]
    assert deleted_document.id == 10
    assert deleted_document.filename == "remove-me.md"


def test_delete_document_raises_when_database_delete_fails() -> None:
    document = _make_document(document_id=3)
    db = MagicMock()
    db.get.return_value = document
    db.commit.side_effect = RuntimeError("database unavailable")

    with pytest.raises(DocumentDeletionError, match="Document 3 could not be deleted"):
        delete_document(db, 3)

    db.rollback.assert_called_once()


@patch("app.api.routes.documents.delete_document")
def test_delete_document_endpoint_returns_success(
    mock_delete_document: MagicMock,
    client: TestClient,
) -> None:
    mock_delete_document.return_value = DocumentDeleteResponse(
        document_id=12,
        filename="test-notes.md",
        deleted=True,
    )

    response = client.delete("/api/v1/documents/12")

    assert response.status_code == 200
    assert response.json() == {
        "document_id": 12,
        "filename": "test-notes.md",
        "deleted": True,
    }


@patch("app.api.routes.documents.delete_document")
def test_delete_document_endpoint_returns_not_found(
    mock_delete_document: MagicMock,
    client: TestClient,
) -> None:
    mock_delete_document.side_effect = DocumentNotFoundError(99)

    response = client.delete("/api/v1/documents/99")

    assert response.status_code == 404
    assert response.json()["detail"] == "Document 99 was not found."
