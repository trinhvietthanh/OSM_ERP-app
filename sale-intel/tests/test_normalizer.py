from decimal import Decimal

from src.normalization.normalizer import (
    discount_percent,
    normalize_product,
    normalize_promotion,
    url_hash,
)
from src.normalization.promotion_type import PromotionType, classify_promotion
from src.parsers.base import ParsedProduct, ParsedPromotion


def test_classify_promotion_spec_examples():
    assert classify_promotion("60% off select accessories") is PromotionType.PERCENT_OFF
    assert classify_promotion("$14.99 select women's styles") is PromotionType.FIXED_PRICE
    assert classify_promotion("Buy 3 Get 1 Free") is PromotionType.BUY_X_GET_Y
    assert classify_promotion("Free Shipping on $50+") is PromotionType.FREE_SHIPPING


def test_classify_promotion_more_cases():
    assert classify_promotion("Extra 20% off with code SAVE20") is PromotionType.COUPON_CODE
    assert classify_promotion("Take 25% off", code="TAKE25") is PromotionType.COUPON_CODE
    assert classify_promotion("Clearance up to 75% off") is PromotionType.CLEARANCE
    assert classify_promotion("Flash sale — today only") is PromotionType.LIMITED_TIME
    assert classify_promotion("BOGO 50% mist") is PromotionType.BUY_X_GET_Y
    assert classify_promotion("New arrivals") is PromotionType.UNKNOWN


def test_clearance_beats_percent():
    # "Clearance up to 75% off" is clearance, not plain percent_off.
    assert classify_promotion("Clearance — up to 75% off select items") is PromotionType.CLEARANCE


def test_url_hash_canonicalizes():
    a = url_hash("https://usa.tommy.com/en/shirt-123?color=blue&utm=x#top")
    b = url_hash("https://usa.tommy.com/en/shirt-123/")
    assert a == b


def test_discount_percent():
    assert discount_percent(Decimal("100"), Decimal("60")) == 40.0
    assert discount_percent(None, Decimal("60")) is None
    assert discount_percent(Decimal("50"), Decimal("60")) is None  # bogus strike


def test_normalize_product_drops_unusable_and_fixes_swapped_prices():
    assert normalize_product(
        ParsedProduct(source_id="x", name="", url="https://x", current_price=Decimal("1"))
    ) is None
    assert normalize_product(
        ParsedProduct(source_id="x", name="A", url="https://x", current_price=None)
    ) is None

    swapped = normalize_product(
        ParsedProduct(
            source_id="x",
            name="A",
            url="https://x/a",
            original_price=Decimal("10"),
            current_price=Decimal("20"),
        )
    )
    assert swapped is not None
    assert swapped.dto.original_price is None  # bogus original dropped
    assert swapped.discount_percent is None


def test_normalize_promotion_classifies():
    normalized = normalize_promotion(
        ParsedPromotion(source_id="x", title="Buy 3 Get 1 Free body care")
    )
    assert normalized is not None
    assert normalized.promotion_type is PromotionType.BUY_X_GET_Y
    assert normalized.content_hash
