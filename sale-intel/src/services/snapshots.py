import hashlib
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from src.collectors.base import CollectorResult
from src.db.models import RawSnapshot
from src.storage.base import ObjectStorage


async def store_snapshot(
    session: AsyncSession,
    storage: ObjectStorage,
    result: CollectorResult,
    parser_version: str | None = None,
) -> RawSnapshot:
    """Persist raw bytes to object storage and the pointer row to Postgres."""
    digest = hashlib.sha256(result.raw_content).hexdigest()
    ts = result.collected_at.strftime("%Y%m%d/%H%M%S")
    extension = "json" if "json" in result.content_type else "html"
    key = f"{result.source_id}/{ts}_{digest[:12]}.{extension}"
    storage_path = storage.put(key, result.raw_content, result.content_type)

    snapshot = RawSnapshot(
        source_id=result.source_id,
        url=result.url,
        content_type=result.content_type,
        storage_path=storage_path,
        content_hash=digest,
        status_code=result.status_code,
        parser_version=parser_version,
        collected_at=result.collected_at or datetime.now(UTC),
    )
    session.add(snapshot)
    await session.flush()
    return snapshot
