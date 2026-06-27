from abc import ABC, abstractmethod
from contextlib import contextmanager
from collections.abc import Iterator
from pathlib import Path


class StorageBackend(ABC):
    @abstractmethod
    def save(self, key: str, data: bytes, *, content_type: str | None = None) -> str:
        """Persist file bytes and return the storage key."""

    @abstractmethod
    def read(self, key: str) -> bytes:
        """Read stored file bytes."""

    @abstractmethod
    def delete(self, key: str) -> None:
        """Delete a stored file."""

    @abstractmethod
    def exists(self, key: str) -> bool:
        """Return whether the storage key exists."""

    @abstractmethod
    def check_availability(self) -> bool:
        """Return whether the storage provider is reachable."""

    @contextmanager
    def materialize(self, key: str) -> Iterator[Path]:
        """Provide a local filesystem path suitable for text extraction."""
        with self._materialize(key) as path:
            yield path

    @contextmanager
    @abstractmethod
    def _materialize(self, key: str) -> Iterator[Path]:
        """Backend-specific materialization implementation."""


def build_document_storage_key(document_id: int, filename: str) -> str:
    safe_filename = Path(filename).name
    return f"{document_id}/{safe_filename}"


def content_type_for_file_type(file_type: str) -> str:
    match file_type.lower():
        case "pdf":
            return "application/pdf"
        case "txt":
            return "text/plain"
        case "markdown":
            return "text/markdown"
        case _:
            return "application/octet-stream"
