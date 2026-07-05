from decimal import Decimal

from src.parsers.bbw import BbwSalePageParser, BbwTopOffersParser
from src.parsers.macys import MacysDealsPageParser, MacysSaleListingParser
from src.parsers.tommy import TommyCouponPageParser, TommySaleListingParser


def test_tommy_coupon_page_parser(fixture_html):
    result = TommyCouponPageParser().parse(
        fixture_html("tommy_coupons.html"), "https://usa.tommy.com/en/coupons"
    )
    assert not result.errors
    codes = {c.code for c in result.parsed_coupons}
    assert {"SAVE20", "SHIPFREE", "TAKE25"} <= codes

    save20 = next(c for c in result.parsed_coupons if c.code == "SAVE20")
    assert save20.discount_type == "percent"
    assert save20.discount_value == Decimal("20")

    shipfree = next(c for c in result.parsed_coupons if c.code == "SHIPFREE")
    assert shipfree.min_order_value == Decimal("100")

    take25 = next(c for c in result.parsed_coupons if c.code == "TAKE25")
    assert take25.discount_type == "fixed"
    assert take25.discount_value == Decimal("25")
    assert take25.min_order_value == Decimal("150")  # not the "$25 Off" heading

    # The no-code banner lands in promotions instead.
    assert any("60% off" in p.raw_text for p in result.parsed_promotions)


def test_tommy_sale_listing_parser(fixture_html):
    result = TommySaleListingParser().parse(
        fixture_html("tommy_sale.html"), "https://usa.tommy.com/en/sale"
    )
    assert len(result.parsed_products) == 3
    by_name = {p.name: p for p in result.parsed_products}

    shirt = by_name["Regular Fit Oxford Shirt"]
    assert shirt.original_price == Decimal("79.50")
    assert shirt.current_price == Decimal("39.99")
    assert shirt.url.startswith("https://usa.tommy.com/")
    assert shirt.external_product_id == "TH-78100541"

    socks = by_name["TH Flag Crew Socks 3-Pack"]
    assert socks.original_price is None
    assert socks.current_price == Decimal("14.99")


def test_bbw_top_offers_parser(fixture_html):
    result = BbwTopOffersParser().parse(
        fixture_html("bbw_top_offers.html"), "https://www.bathandbodyworks.com/c/top-offers"
    )
    texts = " | ".join(p.raw_text for p in result.parsed_promotions)
    assert "Buy 3 Get 1 Free" in texts
    assert "Free Shipping on $50+" in texts
    codes = {c.code for c in result.parsed_coupons}
    assert "BRIGHTDAYS" in codes


def test_bbw_sale_page_parser(fixture_html):
    result = BbwSalePageParser().parse(
        fixture_html("bbw_sale.html"), "https://www.bathandbodyworks.com/c/sale"
    )
    assert len(result.parsed_products) == 2
    candle = next(
        p for p in result.parsed_products if "Candle" in p.name
    )
    assert candle.original_price == Decimal("26.95")
    assert candle.current_price == Decimal("12.95")
    # Clearance banner captured as promotion.
    assert any("Clearance" in (p.raw_text or "") for p in result.parsed_promotions)


def test_macys_deals_page_parser(fixture_html):
    result = MacysDealsPageParser().parse(
        fixture_html("macys_deals.html"), "https://www.macys.com/shop/deals-promotions"
    )
    codes = {c.code for c in result.parsed_coupons}
    assert "VIP" in codes
    texts = " | ".join(p.raw_text for p in result.parsed_promotions)
    assert "Buy 2, Get 1 Free" in texts
    assert "Free Shipping on $25+" in texts


def test_macys_sale_listing_parser_json_ld(fixture_html):
    result = MacysSaleListingParser().parse(
        fixture_html("macys_sale.html"), "https://www.macys.com/shop/sale"
    )
    assert len(result.parsed_products) == 2
    suit = next(p for p in result.parsed_products if "Suit" in p.name)
    assert suit.brand == "Calvin Klein"
    assert suit.current_price == Decimal("199.99")
    assert suit.external_product_id == "MCY-11223344"


def test_parsers_never_raise_on_garbage():
    for parser in (
        TommyCouponPageParser(),
        TommySaleListingParser(),
        BbwTopOffersParser(),
        BbwSalePageParser(),
        MacysDealsPageParser(),
        MacysSaleListingParser(),
    ):
        result = parser.parse("<<<not html>>>", "https://example.com")
        assert result.is_empty
        assert result.errors
