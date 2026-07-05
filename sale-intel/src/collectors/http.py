import asyncio
from datetime import UTC, datetime

import httpx

from src.collectors.base import BaseCollector, CollectorResult
from src.settings import get_settings


class HttpCollector(BaseCollector):
    """Polite httpx-based collector.

    A per-collector lock plus ``min_delay_seconds`` keeps request rates low;
    non-2xx responses are returned (not raised) so callers can decide whether
    to fall back to a browser fetch or just record the failure.
    """

    def __init__(
        self,
        source_id: str,
        *,
        min_delay_seconds: float | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> None:
        settings = get_settings()
        self.source_id = source_id
        self._min_delay = (
            min_delay_seconds
            if min_delay_seconds is not None
            else settings.min_delay_seconds
        )
        self._timeout = settings.http_timeout_seconds
        self._headers = {
            "User-Agent": settings.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/json;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.8",
            **(extra_headers or {}),
        }
        self._lock = asyncio.Lock()
        self._last_request_at: float = 0.0

    async def collect(self, url: str) -> CollectorResult:
        async with self._lock:
            loop = asyncio.get_running_loop()
            wait = self._min_delay - (loop.time() - self._last_request_at)
            if wait > 0:
                await asyncio.sleep(wait)
            self._last_request_at = loop.time()

        async with httpx.AsyncClient(
            headers=self._headers, timeout=self._timeout, follow_redirects=True
        ) as client:
            response = await client.get(url)

        return CollectorResult(
            source_id=self.source_id,
            url=str(response.url),
            content_type=response.headers.get("content-type", "text/html"),
            raw_content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers),
            collected_at=datetime.now(UTC),
            metadata={"collector": "http", "requested_url": url},
        )
