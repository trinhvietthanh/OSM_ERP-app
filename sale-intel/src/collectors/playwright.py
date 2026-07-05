from datetime import UTC, datetime

from src.collectors.base import BaseCollector, CollectorResult
from src.settings import get_settings


class PlaywrightCollector(BaseCollector):
    """Headless-browser fallback for JS-rendered pages.

    Uses a plain Chromium context with the same declared User-Agent as the
    HTTP collector — the goal is rendering JavaScript, NOT evading bot
    detection. If the site still blocks the request, the blocked response is
    returned unchanged.

    Playwright is an optional dependency: install with
    ``uv add playwright && uv run playwright install chromium``.
    """

    def __init__(self, source_id: str) -> None:
        self.source_id = source_id

    async def collect(self, url: str) -> CollectorResult:
        try:
            from playwright.async_api import async_playwright
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError(
                "PlaywrightCollector requires the 'playwright' package: "
                "uv add playwright && uv run playwright install chromium"
            ) from exc

        settings = get_settings()
        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=True)
            try:
                context = await browser.new_context(user_agent=settings.user_agent)
                page = await context.new_page()
                response = await page.goto(
                    url, timeout=settings.http_timeout_seconds * 1000
                )
                html = await page.content()
                status = response.status if response is not None else 0
                headers = dict(response.headers) if response is not None else {}
            finally:
                await browser.close()

        return CollectorResult(
            source_id=self.source_id,
            url=url,
            content_type="text/html",
            raw_content=html.encode("utf-8"),
            status_code=status,
            headers=headers,
            collected_at=datetime.now(UTC),
            metadata={"collector": "playwright", "requested_url": url},
        )
