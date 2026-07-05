"""Promotion-type classification.

Order matters: the most specific signals win (an offer with a coupon code is
a coupon_code promotion even if it also says "25% off").
"""

import re
from enum import Enum


class PromotionType(str, Enum):
    PERCENT_OFF = "percent_off"
    FIXED_PRICE = "fixed_price"
    BUY_X_GET_Y = "buy_x_get_y"
    FREE_SHIPPING = "free_shipping"
    COUPON_CODE = "coupon_code"
    CLEARANCE = "clearance"
    LIMITED_TIME = "limited_time"
    UNKNOWN = "unknown"


_BUY_X_GET_Y_RE = re.compile(
    r"\bbuy\s+\d+\s*,?\s*get\s+\d+|\bb\d+g\d+\b|\bbogo\b", re.IGNORECASE
)
_PERCENT_RE = re.compile(r"\d{1,2}\s*%\s*off", re.IGNORECASE)
_FIXED_PRICE_RE = re.compile(
    r"\$\s*[\d,]+(?:\.\d{1,2})?\s+(?:select|off\b|\w+(?:'s)?\s+(?:styles?|items?|body|care|candles?|mist))",
    re.IGNORECASE,
)
_FREE_SHIPPING_RE = re.compile(r"free\s+shipping", re.IGNORECASE)
_CLEARANCE_RE = re.compile(r"\bclearance\b", re.IGNORECASE)
_LIMITED_RE = re.compile(
    r"limited\s+time|today\s+only|ends\s+(?:tonight|today|soon)|flash\s+sale",
    re.IGNORECASE,
)
_CODE_RE = re.compile(r"\b(?:code|coupon)\b", re.IGNORECASE)


def classify_promotion(text: str, code: str | None = None) -> PromotionType:
    """Map free-form promo text (plus optional explicit code) to the enum."""
    if code or _CODE_RE.search(text):
        return PromotionType.COUPON_CODE
    if _BUY_X_GET_Y_RE.search(text):
        return PromotionType.BUY_X_GET_Y
    if _FREE_SHIPPING_RE.search(text):
        return PromotionType.FREE_SHIPPING
    # Clearance outranks a bare percent: "Clearance — up to 75% off" is a
    # clearance event that happens to quote a percentage.
    if _CLEARANCE_RE.search(text):
        return PromotionType.CLEARANCE
    if _PERCENT_RE.search(text):
        return PromotionType.PERCENT_OFF
    if _FIXED_PRICE_RE.search(text):
        return PromotionType.FIXED_PRICE
    if _LIMITED_RE.search(text):
        return PromotionType.LIMITED_TIME
    return PromotionType.UNKNOWN
