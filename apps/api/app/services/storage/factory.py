from functools import lru_cache

from app.config.settings import Settings, settings
from app.services.storage.base import StorageBackend
from app.services.storage.local_storage import LocalStorageBackend
from app.services.storage.supabase_storage import SupabaseStorageBackend


def create_storage_backend(app_settings: Settings) -> StorageBackend:
    if app_settings.storage_provider == "supabase":
        if not app_settings.supabase_storage_configured:
            raise RuntimeError(
                "Supabase storage is selected but required credentials are missing."
            )
        return SupabaseStorageBackend(
            supabase_url=app_settings.supabase_url or "",
            service_role_key=app_settings.supabase_service_role_key or "",
            bucket=app_settings.supabase_storage_bucket or "",
        )

    return LocalStorageBackend(upload_dir=app_settings.upload_dir)


@lru_cache
def get_storage_backend() -> StorageBackend:
    return create_storage_backend(settings)


def reset_storage_backend_cache() -> None:
    get_storage_backend.cache_clear()
