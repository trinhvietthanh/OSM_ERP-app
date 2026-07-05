"""End-to-end pipeline demo without hitting live sites.

Feeds fixture HTML through the exact production path
(snapshot → parser → normalizer → ingest), then re-ingests Tommy's sale page
with lowered prices to demonstrate price-change detection + deal events +
alert firing.

Run: uv run python scripts/demo_ingest.py
"""

import asyncio
import re
import sys
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import func, select  # noqa: E402

from src.collectors.base import CollectorResult  # noqa: E402
from src.db import models  # noqa: E402
from src.db.session import AsyncSessionFactory  # noqa: E402
from src.parsers.registry import get_parser  # noqa: E402
from src.services.ingest import ingest_parser_result  # noqa: E402
from src.services.snapshots import store_snapshot  # noqa: E402
from src.storage.factory import get_object_storage  # noqa: E402

FIXTURES = Path(__file__).resolve().parent.parent / "tests" / "fixtures"

RUNS = [
    ("tommy_us", "tommy_coupons.html", "tommy_coupon_page_parser",
     "https://usa.tommy.com/en/tommy-hilfiger-coupons"),
    ("tommy_us", "tommy_sale.html", "tommy_sale_listing_parser",
     "https://usa.tommy.com/en/sale"),
    ("bbw_us", "bbw_top_offers.html", "bbw_top_offers_parser",
     "https://www.bathandbodyworks.com/c/top-offers"),
    ("bbw_us", "bbw_sale.html", "bbw_sale_page_parser",
     "https://www.bathandbodyworks.com/c/sale"),
    ("macys_us", "macys_deals.html", "macys_deals_page_parser",
     "https://www.macys.com/shop/deals-promotions"),
    ("macys_us", "macys_sale.html", "macys_sale_listing_parser",
     "https://www.macys.com/shop/sale"),
]


async def ingest_html(session, source_id, html, parser_name, url):
    parser = get_parser(parser_name)
    fake = CollectorResult(
        source_id=source_id,
        url=url,
        content_type="text/html",
        raw_content=html.encode(),
        status_code=200,
        headers={},
        collected_at=datetime.now(UTC),
        metadata={"collector": "fixture"},
    )
    await store_snapshot(session, get_object_storage(), fake, parser.parser_version)
    result = parser.parse(html, url)
    return await ingest_parser_result(session, result)


async def main() -> None:
    async with AsyncSessionFactory() as session:
        # An alert rule so the price-drop event actually fires something.
        if not (await session.scalars(select(models.AlertRule))).first():
            session.add(
                models.AlertRule(
                    name="Big drops (>=20%)",
                    rule_type="price_drop_percent",
                    config={"min_discount_percent": 20},
                )
            )

        print("=== pass 1: initial ingest of all fixtures ===")
        for source_id, fixture, parser_name, url in RUNS:
            stats = await ingest_html(
                session, source_id, (FIXTURES / fixture).read_text(), parser_name, url
            )
            print(f"  {fixture:24} {dict(stats)}")

        print("\n=== pass 2: Tommy prices drop 30% → deal events ===")
        html = (FIXTURES / "tommy_sale.html").read_text()
        html = html.replace("$39.99", "$27.99").replace("$54.99", "$37.99")
        stats = await ingest_html(
            session, "tommy_us", html, "tommy_sale_listing_parser",
            "https://usa.tommy.com/en/sale",
        )
        print(f"  tommy_sale (repriced)    {dict(stats)}")

        await session.commit()

        print("\n=== totals ===")
        for model in (
            models.RawSnapshot, models.Product, models.PriceSnapshot,
            models.Promotion, models.Coupon, models.DealEvent, models.AlertLog,
        ):
            count = await session.scalar(select(func.count()).select_from(model))
            print(f"  {model.__tablename__:20} {count}")

        print("\n=== fired alerts ===")
        for log in (await session.scalars(select(models.AlertLog))).all():
            print(f"  {log.message}")


if __name__ == "__main__":
    asyncio.run(main())
