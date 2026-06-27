import logging
import shutil
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from app.services.storage.base import StorageBackend

logger = logging.getLogger(__name__)


class LocalStorageBackend(StorageBackend):
    def __init__(self, upload_dir: Path) -> None:
        self.upload_dir = upload_dir

    def _resolve_path(self, key: str) -> Path:
        normalized_key = key.replace("\\", "/").lstrip("/")
        destination = (self.upload_dir / normalized_key).resolve()
        root = self.upload_dir.resolve()

        if root not in destination.parents and destination != root:
            raise ValueError("Storage key resolves outside the upload directory.")

        return destination

    def save(self, key: str, data: bytes, *, content_type: str | None = None) -> str:
        destination = self._resolve_path(key)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(data)
        return key

    def read(self, key: str) -> bytes:
        destination = self._resolve_path(key)
        return destination.read_bytes()

    def delete(self, key: str) -> None:
        destination = self._resolve_path(key)
        parent = destination.parent

        try:
            destination.unlink(missing_ok=True)
            if parent.exists() and parent != self.upload_dir.resolve():
                if not any(parent.iterdir()):
                    parent.rmdir()
        except OSError:
            logger.warning("Could not remove local storage object for key %s", key)

    def exists(self, key: str) -> bool:
        return self._resolve_path(key).exists()

    def check_availability(self) -> bool:
        try:
            self.upload_dir.mkdir(parents=True, exist_ok=True)
            probe = self.upload_dir / ".storage_probe"
            probe.write_text("ok", encoding="utf-8")
            probe.unlink(missing_ok=True)
            return True
        except OSError:
            logger.exception("Local storage availability check failed")
            return False

    @contextmanager
    def _materialize(self, key: str) -> Iterator[Path]:
        yield self._resolve_path(key)
