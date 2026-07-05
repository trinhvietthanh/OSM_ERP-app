"""Source-specific collectors: HTTP first, Playwright fallback when the page
needs JS rendering (empty/challenge shell) — never to defeat a hard block."""

from src.collectors.base import BaseCollector, CollectorResult
from src.collectors.http import HttpCollector
from src.collectors.playwright import PlaywrightCollector

#: Status codes where a browser retry is pointless or would amount to
#: working around an explicit block — we record the failure instead.
_HARD_BLOCK_STATUSES = {401, 403, 429}


class FallbackCollector(BaseCollector):
    """HTTP first; fall back to Playwright only when HTML came back OK but
    looks like an empty JS shell (no meaningful body content)."""

    def __init__(self, source_id: str, **http_kwargs) -> None:
        self.source_id = source_id
        self._http = HttpCollector(source_id, **http_kwargs)
        self._playwright = PlaywrightCollector(source_id)

    async def collect(self, url: str) -> CollectorResult:
        result = await self._http.collect(url)
        if self._needs_browser(result):
            try:
                browser_result = await self._playwright.collect(url)
            except RuntimeError:
                # Playwright not installed — return what HTTP gave us.
                result.metadata["playwright_fallback"] = "unavailable"
                return result
            browser_result.metadata["fallback_from_status"] = result.status_code
            return browser_result
        return result

    @staticmethod
    def _needs_browser(result: CollectorResult) -> bool:
        if result.status_code in _HARD_BLOCK_STATUSES:
            return False
        if not result.ok:
            return True
        if "html" not in result.content_type:
            return False
        # Heuristic: a served page whose body is a near-empty JS shell.
        return len(result.raw_content) < 5_000


class MacysCollector(FallbackCollector):
    def __init__(self) -> None:
        super().__init__("macys_us", min_delay_seconds=3.0)


class TommyCollector(FallbackCollector):
    def __init__(self) -> None:
        super().__init__("tommy_us", min_delay_seconds=3.0)


class BbwCollector(FallbackCollector):
    def __init__(self) -> None:
        super().__init__("bbw_us", min_delay_seconds=3.0)


_COLLECTORS: dict[str, type[FallbackCollector]] = {
    "macys_us": MacysCollector,
    "tommy_us": TommyCollector,
    "bbw_us": BbwCollector,
}


def get_collector(source_id: str) -> BaseCollector:
    collector_cls = _COLLECTORS.get(source_id)
    if collector_cls is not None:
        return collector_cls()
    return FallbackCollector(source_id)
