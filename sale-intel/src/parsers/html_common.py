"""Shared conservative HTML extraction used by all source parsers.

Retail markup shifts constantly, so instead of pinning exact class names we
scan for *shape*: promo-looking blocks with money/percent patterns, product
tiles with a link + price, and schema.org JSON-LD when present. Each source
parser only supplies selectors/hints.
"""

import json
import re
from decimal import Decimal, InvalidOperation
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag

from src.parsers.base import (
    ParsedCoupon,
    ParsedProduct,
    ParsedPromotion,
    clean_text,
    extract_all_prices,
    extract_coupon_code,
)

PROMO_TEXT_RE = re.compile(
    r"(\d+%\s*off|\$\s*[\d,.]+|buy\s+\d+.*get|free\s+shipping|clearance|sale)",
    re.IGNORECASE,
)
PERCENT_RE = re.compile(r"(\d{1,2})\s*%\s*off", re.IGNORECASE)
# Minimum-spend threshold. Require an explicit qualifier ("orders of/over $X"
# or "on $X+") so a bare price elsewhere in the block ("$25 Off Your Order")
# is not mistaken for a minimum.
MIN_ORDER_RE = re.compile(
    r"(?:orders?\s+(?:of|over)\s*|on\s+)\$\s*([\d,]+)\s*\+?", re.IGNORECASE
)


def make_soup(raw_content: str) -> BeautifulSoup:
    return BeautifulSoup(raw_content, "lxml")


def find_promo_blocks(soup: BeautifulSoup, extra_selector: str = "") -> list[Tag]:
    """Candidate promo/coupon blocks: marked-up as such, or promo-shaped text."""
    selector = (
        '[class*="coupon"], [class*="promo"], [class*="offer"], [class*="deal"]'
    )
    if extra_selector:
        selector = f"{selector}, {extra_selector}"
    seen: set[int] = set()
    blocks: list[Tag] = []
    for tag in soup.select(selector):
        # Skip children of an already-accepted block.
        if any(id(parent) in seen for parent in tag.parents):
            continue
        # A wrapper holding several offers (≥2 headings) is too coarse —
        # let its child blocks match individually instead.
        if len(tag.find_all(["h1", "h2", "h3", "h4"])) > 1:
            continue
        text = clean_text(tag.get_text(" "))
        if 10 <= len(text) <= 500 and PROMO_TEXT_RE.search(text):
            seen.add(id(tag))
            blocks.append(tag)
    return blocks


def block_to_promotion(
    block: Tag, source_id: str, source_url: str
) -> ParsedPromotion:
    text = clean_text(block.get_text(" "))
    heading = block.find(["h1", "h2", "h3", "h4", "strong"])
    title = clean_text(heading.get_text(" ")) if heading else text[:120]
    return ParsedPromotion(
        source_id=source_id,
        title=title or text[:120],
        raw_text=text,
        code=extract_coupon_code(text),
        condition_text=_condition_from_text(text),
        source_url=source_url,
    )


def block_to_coupon(block: Tag, source_id: str, source_url: str) -> ParsedCoupon | None:
    """A promo block that carries a code becomes a coupon."""
    text = clean_text(block.get_text(" "))
    code = extract_coupon_code(text)
    if code is None:
        return None
    discount_type: str | None = None
    discount_value: Decimal | None = None
    if match := PERCENT_RE.search(text):
        discount_type = "percent"
        discount_value = Decimal(match.group(1))
    elif "free shipping" in text.lower():
        discount_type = "free_shipping"
    else:
        prices = extract_all_prices(text)
        if prices:
            discount_type = "fixed"
            discount_value = prices[0]
    min_order: Decimal | None = None
    if match := MIN_ORDER_RE.search(text):
        try:
            min_order = Decimal(match.group(1).replace(",", ""))
        except InvalidOperation:
            min_order = None
    return ParsedCoupon(
        source_id=source_id,
        code=code,
        discount_type=discount_type,
        discount_value=discount_value,
        min_order_value=min_order,
        condition_text=_condition_from_text(text),
        source_url=source_url,
    )


def _condition_from_text(text: str) -> str | None:
    """Trailing qualifier ('select styles', 'exclusions apply', …) if any."""
    match = re.search(
        r"((?:select|excludes?|exclusions?|valid|online only|in stores)[^.!]*)",
        text,
        re.IGNORECASE,
    )
    return clean_text(match.group(1)) if match else None


# ------------------------------------------------------------- product tiles


def find_product_tiles(soup: BeautifulSoup, extra_selector: str = "") -> list[Tag]:
    selector = '[class*="product-tile"], [class*="productTile"], li[class*="product"], div[class*="product-card"], article[class*="product"]'
    if extra_selector:
        selector = f"{selector}, {extra_selector}"
    seen: set[int] = set()
    tiles: list[Tag] = []
    for tag in soup.select(selector):
        if any(id(parent) in seen for parent in tag.parents):
            continue
        if tag.find("a", href=True) and extract_all_prices(tag.get_text(" ")):
            seen.add(id(tag))
            tiles.append(tag)
    return tiles


def tile_to_product(
    tile: Tag, source_id: str, base_url: str, currency: str = "USD"
) -> ParsedProduct | None:
    link = tile.find("a", href=True)
    if link is None:
        return None
    url = urljoin(base_url, link["href"])

    name_tag = tile.select_one(
        '[class*="name"], [class*="title"], h2, h3, h4'
    )
    name = clean_text(name_tag.get_text(" ")) if name_tag else clean_text(
        link.get_text(" ")
    )
    if not name:
        return None

    brand_tag = tile.select_one('[class*="brand"]')
    image = tile.find("img")

    # Struck-through price = original; otherwise min/max of all prices seen.
    original = None
    strike = tile.select_one('del, s, [class*="strike"], [class*="was"], [class*="original"]')
    if strike is not None:
        strike_prices = extract_all_prices(strike.get_text(" "))
        original = strike_prices[0] if strike_prices else None
    prices = extract_all_prices(tile.get_text(" "))
    if not prices:
        return None
    current = min(prices)
    if original is None and len(prices) > 1:
        original = max(prices)

    return ParsedProduct(
        source_id=source_id,
        external_product_id=tile.get("data-product-id") or tile.get("id"),
        name=name,
        brand=clean_text(brand_tag.get_text(" ")) if brand_tag else None,
        url=url,
        image_url=urljoin(base_url, image["src"]) if image and image.get("src") else None,
        original_price=original,
        current_price=current,
        currency=currency,
        raw_metadata={"tile_classes": tile.get("class", [])},
    )


# ----------------------------------------------------------------- JSON-LD


def json_ld_products(
    soup: BeautifulSoup, source_id: str, base_url: str, currency: str = "USD"
) -> list[ParsedProduct]:
    """Products declared via schema.org JSON-LD (most stable signal)."""
    products: list[ParsedProduct] = []
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string or "")
        except (json.JSONDecodeError, TypeError):
            continue
        for node in _iter_ld_nodes(data):
            if node.get("@type") not in ("Product", "IndividualProduct"):
                continue
            offers = node.get("offers") or {}
            if isinstance(offers, list):
                offers = offers[0] if offers else {}
            price = offers.get("price") or offers.get("lowPrice")
            if price is None:
                continue
            try:
                current = Decimal(str(price))
            except InvalidOperation:
                continue
            products.append(
                ParsedProduct(
                    source_id=source_id,
                    external_product_id=str(node.get("sku") or node.get("productID") or "") or None,
                    name=clean_text(str(node.get("name", ""))),
                    brand=_ld_brand(node),
                    url=urljoin(base_url, str(node.get("url", base_url))),
                    image_url=_ld_image(node),
                    current_price=current,
                    currency=str(offers.get("priceCurrency", currency)),
                    raw_metadata={"json_ld": True},
                )
            )
    return [p for p in products if p.name]


def _iter_ld_nodes(data) -> list[dict]:
    if isinstance(data, list):
        out = []
        for item in data:
            out.extend(_iter_ld_nodes(item))
        return out
    if isinstance(data, dict):
        nodes = [data]
        for value in (data.get("itemListElement") or []):
            if isinstance(value, dict):
                nodes.extend(_iter_ld_nodes(value.get("item", value)))
        if "@graph" in data:
            nodes.extend(_iter_ld_nodes(data["@graph"]))
        return nodes
    return []


def _ld_brand(node: dict) -> str | None:
    brand = node.get("brand")
    if isinstance(brand, dict):
        return brand.get("name")
    return brand if isinstance(brand, str) else None


def _ld_image(node: dict) -> str | None:
    image = node.get("image")
    if isinstance(image, list):
        image = image[0] if image else None
    return image if isinstance(image, str) else None
