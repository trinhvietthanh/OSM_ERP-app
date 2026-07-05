"""Bath & Body Works US parsers (conservative; fixture-tested)."""

from src.parsers.base import BaseParser, ParserResult
from src.parsers.html_common import (
    block_to_coupon,
    block_to_promotion,
    find_product_tiles,
    find_promo_blocks,
    json_ld_products,
    make_soup,
    tile_to_product,
)

_BASE_URL = "https://www.bathandbodyworks.com"
_SOURCE_ID = "bbw_us"


class BbwTopOffersParser(BaseParser):
    parser_name = "bbw_top_offers_parser"
    parser_version = "0.1.0"

    def parse(self, raw_content: str, source_url: str = "") -> ParserResult:
        result = ParserResult(metadata={"parser": self.parser_name})
        try:
            soup = make_soup(raw_content)
        except Exception as exc:  # noqa: BLE001
            result.errors.append(f"unparseable html: {exc}")
            return result

        blocks = find_promo_blocks(soup, extra_selector='[class*="banner"], section')
        for block in blocks:
            coupon = block_to_coupon(block, _SOURCE_ID, source_url)
            if coupon is not None:
                result.parsed_coupons.append(coupon)
            result.parsed_promotions.append(
                block_to_promotion(block, _SOURCE_ID, source_url)
            )
        if not blocks:
            result.errors.append("no offer blocks recognized")
        return result


class BbwSalePageParser(BaseParser):
    parser_name = "bbw_sale_page_parser"
    parser_version = "0.1.0"

    def parse(self, raw_content: str, source_url: str = "") -> ParserResult:
        result = ParserResult(metadata={"parser": self.parser_name})
        try:
            soup = make_soup(raw_content)
        except Exception as exc:  # noqa: BLE001
            result.errors.append(f"unparseable html: {exc}")
            return result

        result.parsed_products.extend(json_ld_products(soup, _SOURCE_ID, _BASE_URL))
        if not result.parsed_products:
            for tile in find_product_tiles(soup):
                product = tile_to_product(tile, _SOURCE_ID, _BASE_URL)
                if product is not None:
                    result.parsed_products.append(product)

        for block in find_promo_blocks(soup):
            result.parsed_promotions.append(
                block_to_promotion(block, _SOURCE_ID, source_url)
            )

        if result.is_empty:
            result.errors.append("no products or promotions recognized")
        return result
