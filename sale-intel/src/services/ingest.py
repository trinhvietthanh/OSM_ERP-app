"""Ingest: normalized DTOs → products, price snapshots, promotions, coupons,
deal events and alert evaluation. The only layer that writes business rows."""

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import (
    AlertLog,
    AlertRule,
    Coupon,
    DealEvent,
    PriceSnapshot,
    Product,
    Promotion,
)
from src.normalization.normalizer import (
    normalize_coupon,
    normalize_product,
    normalize_promotion,
)
from src.parsers.base import ParserResult
from src.settings import get_settings


class IngestStats(dict):
    """Simple counters returned to the crawl job."""

    def bump(self, key: str) -> None:
        self[key] = self.get(key, 0) + 1


async def ingest_parser_result(
    session: AsyncSession, result: ParserResult
) -> IngestStats:
    stats = IngestStats()
    now = datetime.now(UTC)

    for parsed in result.parsed_products:
        normalized = normalize_product(parsed)
        if normalized is None:
            stats.bump("products_skipped")
            continue
        await _ingest_product(session, normalized, now, stats)

    for parsed in result.parsed_promotions:
        normalized = normalize_promotion(parsed)
        if normalized is None:
            stats.bump("promotions_skipped")
            continue
        await _ingest_promotion(session, normalized, now, stats)

    for parsed in result.parsed_coupons:
        normalized = normalize_coupon(parsed)
        if normalized is None:
            stats.bump("coupons_skipped")
            continue
        await _ingest_coupon(session, normalized, now, stats)

    return stats


# ---------------------------------------------------------------- products


async def _ingest_product(session, normalized, now, stats: IngestStats) -> None:
    dto = normalized.dto
    product = (
        await session.scalars(
            select(Product).where(
                Product.source_id == dto.source_id,
                Product.url_hash == normalized.url_hash,
            )
        )
    ).one_or_none()

    if product is None:
        product = Product(
            source_id=dto.source_id,
            external_product_id=dto.external_product_id,
            name=dto.name,
            brand=dto.brand,
            category=dto.category,
            url=dto.url,
            url_hash=normalized.url_hash,
            image_url=dto.image_url,
            currency=dto.currency,
            stock_status=dto.stock_status,
            raw_metadata=dto.raw_metadata or None,
            first_seen_at=now,
            last_seen_at=now,
        )
        session.add(product)
        await session.flush()
        stats.bump("products_created")
    else:
        product.name = dto.name
        product.brand = dto.brand or product.brand
        product.image_url = dto.image_url or product.image_url
        product.stock_status = dto.stock_status or product.stock_status
        product.last_seen_at = now
        stats.bump("products_updated")

    # Latest snapshot → change detection before inserting the new one.
    latest = (
        await session.scalars(
            select(PriceSnapshot)
            .where(PriceSnapshot.product_id == product.id)
            .order_by(PriceSnapshot.collected_at.desc())
            .limit(1)
        )
    ).first()

    session.add(
        PriceSnapshot(
            product_id=product.id,
            source_id=dto.source_id,
            original_price=dto.original_price,
            current_price=dto.current_price,
            discount_percent=normalized.discount_percent,
            currency=dto.currency,
            collected_at=now,
        )
    )
    stats.bump("price_snapshots")

    if latest is not None and latest.current_price != dto.current_price:
        stats.bump("price_changes")
        drop_pct = (
            float((latest.current_price - dto.current_price) / latest.current_price)
            * 100
            if latest.current_price > 0
            else 0.0
        )
        if drop_pct >= get_settings().price_drop_threshold_pct:
            event = DealEvent(
                source_id=dto.source_id,
                product_id=product.id,
                event_type="price_drop",
                old_price=latest.current_price,
                new_price=dto.current_price,
                discount_percent=round(drop_pct, 2),
                payload={"product_name": dto.name, "url": dto.url},
            )
            session.add(event)
            await session.flush()
            stats.bump("deal_events")
            await _evaluate_alerts(session, event, stats)


# --------------------------------------------------------------- promotions


async def _ingest_promotion(session, normalized, now, stats: IngestStats) -> None:
    dto = normalized.dto
    existing = (
        await session.scalars(
            select(Promotion).where(
                Promotion.source_id == dto.source_id,
                Promotion.content_hash == normalized.content_hash,
            )
        )
    ).one_or_none()
    if existing is not None:
        existing.last_seen_at = now
        existing.is_active = True
        stats.bump("promotions_seen_again")
        return
    session.add(
        Promotion(
            source_id=dto.source_id,
            title=dto.title[:512],
            promotion_type=normalized.promotion_type.value,
            raw_text=dto.raw_text,
            code=dto.code,
            start_at=dto.start_at,
            end_at=dto.end_at,
            condition_text=dto.condition_text,
            source_url=dto.source_url,
            content_hash=normalized.content_hash,
            first_seen_at=now,
            last_seen_at=now,
        )
    )
    stats.bump("promotions_created")


async def _ingest_coupon(session, normalized, now, stats: IngestStats) -> None:
    dto = normalized.dto
    existing = (
        await session.scalars(
            select(Coupon).where(
                Coupon.source_id == dto.source_id,
                Coupon.content_hash == normalized.content_hash,
            )
        )
    ).one_or_none()
    if existing is not None:
        existing.is_active = True
        stats.bump("coupons_seen_again")
        return
    session.add(
        Coupon(
            source_id=dto.source_id,
            code=dto.code,
            discount_type=dto.discount_type,
            discount_value=dto.discount_value,
            min_order_value=dto.min_order_value,
            max_discount_value=dto.max_discount_value,
            condition_text=dto.condition_text,
            start_at=dto.start_at,
            end_at=dto.end_at,
            source_url=dto.source_url,
            content_hash=normalized.content_hash,
        )
    )
    stats.bump("coupons_created")


# ------------------------------------------------------------------ alerts


async def _evaluate_alerts(
    session: AsyncSession, event: DealEvent, stats: IngestStats
) -> None:
    """MVP alerting: fire active rules whose threshold the event clears."""
    rules = (
        await session.scalars(select(AlertRule).where(AlertRule.is_active.is_(True)))
    ).all()
    for rule in rules:
        if rule.rule_type == "price_drop_percent":
            threshold = float(rule.config.get("min_discount_percent", 0))
            if (event.discount_percent or 0) < threshold:
                continue
        elif rule.rule_type == "source":
            if event.source_id not in rule.config.get("source_ids", []):
                continue
        else:
            continue
        session.add(
            AlertLog(
                alert_rule_id=rule.id,
                deal_event_id=event.id,
                channel="log",
                message=(
                    f"[{rule.name}] {event.source_id}: "
                    f"{(event.payload or {}).get('product_name', 'product')} "
                    f"dropped {event.discount_percent}% "
                    f"({event.old_price} -> {event.new_price})"
                ),
            )
        )
        stats.bump("alerts_fired")
