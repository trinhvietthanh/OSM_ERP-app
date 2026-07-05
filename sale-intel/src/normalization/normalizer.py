"""Normalizers: parsed DTOs → clean domain values ready for persistence."""

import hashlib
from dataclasses import dataclass
from decimal import Decimal

from src.normalization.promotion_type import PromotionType, classify_promotion
from src.parsers.base import ParsedCoupon, ParsedProduct, ParsedPromotion


def url_hash(url: str) -> str:
    """Canonical product identity: hash of the URL without query/fragment."""
    canonical = url.split("?")[0].split("#")[0].rstrip("/").lower()
    return hashlib.sha256(canonical.encode()).hexdigest()


def content_hash(*parts: str | None) -> str:
    joined = "|".join((p or "").strip().lower() for p in parts)
    return hashlib.sha256(joined.encode()).hexdigest()


def discount_percent(
    original: Decimal | None, current: Decimal | None
) -> float | None:
    if original is None or current is None or original <= 0 or current > original:
        return None
    return round(float((original - current) / original * 100), 2)


@dataclass(slots=True)
class NormalizedProduct:
    dto: ParsedProduct
    url_hash: str
    discount_percent: float | None


@dataclass(slots=True)
class NormalizedPromotion:
    dto: ParsedPromotion
    promotion_type: PromotionType
    content_hash: str


@dataclass(slots=True)
class NormalizedCoupon:
    dto: ParsedCoupon
    content_hash: str


def normalize_product(dto: ParsedProduct) -> NormalizedProduct | None:
    """Drop unusable rows (no name/url/price); compute identity + discount."""
    if not dto.name or not dto.url or dto.current_price is None:
        return None
    if dto.current_price <= 0:
        return None
    original = dto.original_price
    if original is not None and original < dto.current_price:
        # Swapped or bogus strike-through — keep the sane part only.
        original = None
    dto.original_price = original
    return NormalizedProduct(
        dto=dto,
        url_hash=url_hash(dto.url),
        discount_percent=discount_percent(original, dto.current_price),
    )


def normalize_promotion(dto: ParsedPromotion) -> NormalizedPromotion | None:
    if not dto.title:
        return None
    text = dto.raw_text or dto.title
    promo_type = (
        PromotionType(dto.promotion_type)
        if dto.promotion_type in PromotionType._value2member_map_
        else classify_promotion(text, dto.code)
    )
    return NormalizedPromotion(
        dto=dto,
        promotion_type=promo_type,
        content_hash=content_hash(dto.title, dto.code, dto.condition_text),
    )


def normalize_coupon(dto: ParsedCoupon) -> NormalizedCoupon | None:
    if not dto.code and not dto.condition_text:
        return None
    return NormalizedCoupon(
        dto=dto,
        content_hash=content_hash(
            dto.code,
            str(dto.discount_value) if dto.discount_value is not None else None,
            dto.condition_text,
        ),
    )
