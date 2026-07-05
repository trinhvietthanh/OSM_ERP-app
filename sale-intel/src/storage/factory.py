from functools import lru_cache

from src.settings import get_settings
from src.storage.base import ObjectStorage
from src.storage.local import LocalObjectStorage
from src.storage.s3 import S3ObjectStorage


@lru_cache
def get_object_storage() -> ObjectStorage:
    settings = get_settings()
    if settings.storage_backend == "s3":
        return S3ObjectStorage(
            endpoint_url=settings.s3_endpoint_url,
            bucket=settings.s3_bucket,
            access_key=settings.s3_access_key,
            secret_key=settings.s3_secret_key,
        )
    return LocalObjectStorage(settings.storage_local_root)
