"""Crawl runner: collector → raw snapshot → parser → ingest, tracked as a
crawl_jobs row. One entrypoint per run; scheduling is external (cron/worker)."""

from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from src.collectors.sources import get_collector
from src.db.models import CrawlJob
from src.parsers.registry import get_parser
from src.services.ingest import ingest_parser_result
from src.services.snapshots import store_snapshot
from src.source_config import load_all_source_configs
from src.storage.factory import get_object_storage


async def run_crawl(
    session: AsyncSession, source_id: str, entrypoint: str
) -> CrawlJob:
    configs = load_all_source_configs()
    config = configs.get(source_id)
    if config is None:
        raise KeyError(f"Unknown source {source_id!r}")
    ep = config.entrypoints.get(entrypoint)
    if ep is None:
        raise KeyError(
            f"Unknown entrypoint {entrypoint!r} for {source_id!r} "
            f"(have: {sorted(config.entrypoints)})"
        )

    job = CrawlJob(
        source_id=source_id,
        entrypoint=entrypoint,
        url=ep.url,
        status="running",
        started_at=datetime.now(UTC),
    )
    session.add(job)
    await session.flush()

    try:
        parser = get_parser(ep.parser)
        collector = get_collector(source_id)
        result = await collector.collect(ep.url)

        snapshot = await store_snapshot(
            session, get_object_storage(), result, parser.parser_version
        )
        job.snapshot_id = snapshot.id

        if not result.ok:
            job.status = "failed"
            job.error = f"HTTP {result.status_code} (raw snapshot kept)"
        else:
            parsed = parser.parse(
                result.raw_content.decode("utf-8", errors="replace"), url_str(result)
            )
            stats = await ingest_parser_result(session, parsed)
            job.status = "success"
            job.stats = {**stats, "parser_errors": parsed.errors}
    except Exception as exc:  # noqa: BLE001 — job row must record the failure
        job.status = "failed"
        job.error = str(exc)

    job.finished_at = datetime.now(UTC)
    return job


def url_str(result) -> str:  # noqa: ANN001
    return result.url
