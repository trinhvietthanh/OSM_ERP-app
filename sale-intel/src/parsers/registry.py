from src.parsers.base import BaseParser
from src.parsers.bbw import BbwSalePageParser, BbwTopOffersParser
from src.parsers.macys import MacysDealsPageParser, MacysSaleListingParser
from src.parsers.tommy import TommyCouponPageParser, TommySaleListingParser

_PARSERS: dict[str, type[BaseParser]] = {
    parser.parser_name: parser
    for parser in (
        TommyCouponPageParser,
        TommySaleListingParser,
        BbwTopOffersParser,
        BbwSalePageParser,
        MacysDealsPageParser,
        MacysSaleListingParser,
    )
}


def get_parser(parser_name: str) -> BaseParser:
    parser_cls = _PARSERS.get(parser_name)
    if parser_cls is None:
        raise KeyError(
            f"Unknown parser {parser_name!r}. Available: {sorted(_PARSERS)}"
        )
    return parser_cls()
