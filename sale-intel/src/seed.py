"""Seed/refresh the sources table from configs/sources/*.yaml.

Run: uv run python -m src.seed
"""

import asyncio

from sqlalchemy import select

from src.db.models import Source
from src.db.session import AsyncSessionFactory
from src.source_config import load_all_source_configs


async def seed_sources() -> None:
    async with AsyncSessionFactory() as session:
        for config in load_all_source_configs().values():
            existing = (
                await session.scalars(
                    select(Source).where(Source.source_id == config.source_id)
                )
            ).one_or_none()
            if existing is None:
                session.add(
                    Source(
                        source_id=config.source_id,
                        name=config.name,
                        country=config.country,
                        currency=config.currency,
                        base_url=config.base_url,
                        crawl_type=config.crawl_type,
                        crawl_interval_minutes=config.crawl_interval_minutes,
                        is_active=config.enabled,
                    )
                )
                print(f"[seed] created source {config.source_id}")
            else:
                existing.name = config.name
                existing.base_url = config.base_url
                existing.crawl_type = config.crawl_type
                existing.crawl_interval_minutes = config.crawl_interval_minutes
                existing.is_active = config.enabled
                print(f"[seed] updated source {config.source_id}")
        await session.commit()


if __name__ == "__main__":
    asyncio.run(seed_sources())
