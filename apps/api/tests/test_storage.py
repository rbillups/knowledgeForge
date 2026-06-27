from pathlib import Path

import pytest

from app.config.settings import Settings
from app.services.storage.base import build_document_storage_key, content_type_for_file_type
from app.services.storage.factory import create_storage_backend
from app.services.storage.local_storage import LocalStorageBackend


def test_build_document_storage_key_uses_document_id_and_filename() -> None:
    assert build_document_storage_key(12, "../notes.md") == "12/notes.md"


def test_content_type_for_file_type_maps_known_types() -> None:
    assert content_type_for_file_type("pdf") == "application/pdf"
    assert content_type_for_file_type("markdown") == "text/markdown"


def test_local_storage_save_read_delete(tmp_path: Path) -> None:
    backend = LocalStorageBackend(upload_dir=tmp_path)
    key = "5/test-notes.md"

    backend.save(key, b"# Notes", content_type="text/markdown")
    assert backend.exists(key) is True
    assert backend.read(key) == b"# Notes"

    backend.delete(key)
    assert backend.exists(key) is False


def test_local_storage_materialize_returns_existing_path(tmp_path: Path) -> None:
    backend = LocalStorageBackend(upload_dir=tmp_path)
    key = "7/report.txt"
    backend.save(key, b"hello", content_type="text/plain")

    with backend.materialize(key) as path:
        assert path.read_text(encoding="utf-8") == "hello"


def test_create_storage_backend_uses_local_provider_by_default(
    tmp_path: Path,
) -> None:
    app_settings = Settings(
        database_url="postgresql://test:test@localhost:5432/test",
        app_env="development",
        storage_provider="local",
        upload_dir=tmp_path,
    )

    backend = create_storage_backend(app_settings)

    assert isinstance(backend, LocalStorageBackend)


def test_create_storage_backend_uses_supabase_when_configured() -> None:
    from app.services.storage.supabase_storage import SupabaseStorageBackend

    app_settings = Settings(
        database_url="postgresql://test:test@localhost:5432/test",
        app_env="production",
        storage_provider="supabase",
        cors_allowed_origins="https://example.com",
        supabase_url="https://example.supabase.co",
        supabase_service_role_key="service-role-key",
        supabase_storage_bucket="documents",
    )

    backend = create_storage_backend(app_settings)

    assert isinstance(backend, SupabaseStorageBackend)
