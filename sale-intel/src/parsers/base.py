"""Parser contracts and DTOs.

Parsers turn raw HTML/JSON into plain DTOs. They are deliberately
conservative: when the page structure is unknown they return partial data
plus errors, never raise. All parsers are unit-testable against fixture HTML
in ``tests/fixtures``.
"""

import abc
import re
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal, InvalidOperation


@dataclass(slots=True)
class ParsedProduct:
    source_id: str
    name: str
    url: str
    external_product_id: str | None = None
    brand: str | None = None
    category: str | None = None
    image_url: str | None = None
    original_price: Decimal | None = None
    current_price: Decimal | None = None
    currency: str = "USD"
    stock_status: str | None = None
    raw_metadata: dict = field(default_factory=dict)


@dataclass(slots=True)
class ParsedPromotion:
    source_id: str
    title: str
    promotion_type: str | None = None  # normalizer fills/overrides this
    raw_text: str | None = None
    code: str | None = None
    start_at: datetime | None = None
    end_at: datetime | None = None
    condition_text: str | None = None
    source_url: str | None = None


@dataclass(slots=True)
class ParsedCoupon:
    source_id: str
    code: str | None = None
    discount_type: str | None = None  # percent | fixed | free_shipping
    discount_value: Decimal | None = None
    min_order_value: Decimal | None = None
    max_discount_value: Decimal | None = None
    condition_text: str | None = None
    start_at: datetime | None = None
    end_at: datetime | None = None
    source_url: str | None = None


@dataclass(slots=True)
class ParserResult:
    parsed_products: list[ParsedProduct] = field(default_factory=list)
    parsed_promotions: list[ParsedPromotion] = field(default_factory=list)
    parsed_coupons: list[ParsedCoupon] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    @property
    def is_empty(self) -> bool:
        return not (
            self.parsed_products or self.parsed_promotions or self.parsed_coupons
        )


class BaseParser(abc.ABC):
    parser_name: str
    parser_version: str

    @abc.abstractmethod
    def parse(self, raw_content: str, source_url: str = "") -> ParserResult:
        ...


# ------------------------------------------------------------ shared helpers

_PRICE_RE = re.compile(r"\$\s*([\d,]+(?:\.\d{1,2})?)")


def extract_price(text: str) -> Decimal | None:
    """First ``$X[,XXX][.YY]`` amount in *text*, or None."""
    match = _PRICE_RE.search(text)
    if not match:
        return None
    try:
        return Decimal(match.group(1).replace(",", ""))
    except InvalidOperation:
        return None


def extract_all_prices(text: str) -> list[Decimal]:
    out: list[Decimal] = []
    for raw in _PRICE_RE.findall(text):
        try:
            out.append(Decimal(raw.replace(",", "")))
        except InvalidOperation:
            continue
    return out


# Keyword is case-insensitive (scoped inline flag), but the code itself must be
# UPPERCASE — real coupon codes are (SAVE20, SHIPFREE) while prose like
# "No code needed" is not, so it won't be mistaken for a code.
_CODE_RE = re.compile(r"(?i:code|coupon)[:\s]+([A-Z0-9]{3,20})\b")

# Uppercase words that follow "code"/"coupon" in prose but are not codes.
_CODE_STOPWORDS = {"NEEDED", "REQUIRED", "AT", "ONLINE", "IN", "APPLY", "APPLIED"}


def extract_coupon_code(text: str) -> str | None:
    """Coupon code following the word 'code'/'coupon', if uppercase."""
    match = _CODE_RE.search(text)
    if not match:
        return None
    code = match.group(1)
    return None if code in _CODE_STOPWORDS else code


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()
