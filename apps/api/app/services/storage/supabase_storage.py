import logging
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

import httpx

from app.services.storage.base import StorageBackend

logger = logging.getLogger(__name__)


class SupabaseStorageBackend(StorageBackend):
    def __init__(
        self,
        *,
        supabase_url: str,
        service_role_key: str,
        bucket: str,
        timeout_seconds: float = 30.0,
    ) -> None:
        self.base_url = supabase_url.rstrip("/")
        self.bucket = bucket
        self.timeout_seconds = timeout_seconds
        self._headers = {
            "Authorization": f"Bearer {service_role_key}",
            "apikey": service_role_key,
        }

    def _object_url(self, key: str) -> str:
        normalized_key = key.replace("\\", "/").lstrip("/")
        return f"{self.base_url}/storage/v1/object/{self.bucket}/{normalized_key}"

    def save(self, key: str, data: bytes, *, content_type: str | None = None) -> str:
        headers = {
            **self._headers,
            "Content-Type": content_type or "application/octet-stream",
            "x-upsert": "true",
        }
        response = httpx.post(
            self._object_url(key),
            content=data,
            headers=headers,
            timeout=self.timeout_seconds,
        )
        if response.status_code >= 400:
            logger.error(
                "Supabase storage upload failed with status %s",
                response.status_code,
            )
            raise RuntimeError("Unable to save file to cloud storage.")

        return key.replace("\\", "/").lstrip("/")

    def read(self, key: str) -> bytes:
        response = httpx.get(
            self._object_url(key),
            headers=self._headers,
            timeout=self.timeout_seconds,
        )
        if response.status_code == 404:
            raise FileNotFoundError(key)
        if response.status_code >= 400:
            logger.error(
                "Supabase storage read failed with status %s",
                response.status_code,
            )
            raise RuntimeError("Unable to read file from cloud storage.")

        return response.content

    def delete(self, key: str) -> None:
        normalized_key = key.replace("\\", "/").lstrip("/")
        response = httpx.delete(
            f"{self.base_url}/storage/v1/object/{self.bucket}",
            headers={
                **self._headers,
                "Content-Type": "application/json",
            },
            json={"prefixes": [normalized_key]},
            timeout=self.timeout_seconds,
        )
        if response.status_code >= 400:
            logger.warning(
                "Supabase storage delete returned status %s",
                response.status_code,
            )

    def exists(self, key: str) -> bool:
        try:
            self.read(key)
        except FileNotFoundError:
            return False
        except RuntimeError:
            return False
        return True

    def check_availability(self) -> bool:
        try:
            response = httpx.get(
                f"{self.base_url}/storage/v1/bucket/{self.bucket}",
                headers=self._headers,
                timeout=self.timeout_seconds,
            )
            return response.status_code < 400
        except httpx.HTTPError:
            logger.exception("Supabase storage availability check failed")
            return False

    @contextmanager
    def _materialize(self, key: str) -> Iterator[Path]:
        data = self.read(key)
        suffix = Path(key).suffix or ".bin"
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        temp_path = Path(temp_file.name)
        try:
            temp_file.write(data)
            temp_file.close()
            yield temp_path
        finally:
            temp_path.unlink(missing_ok=True)
