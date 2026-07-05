from datetime import UTC, datetime
from typing import Self

from src.modules.campaign.domain.value_objects.campaign_product import (
    CampaignProductId,
    Money,
)
from src.modules.campaign.domain.value_objects.sale_round import SaleRoundId
from src.modules.catalog.domain.value_objects.product import ProductId
from src.modules.organization.domain.value_objects.organization import OrganizationId
from src.shared.domain.base import Entity


class CampaignProduct(Entity[CampaignProductId]):
    """A product offered in a sale round, with that round's price and deposit.

    This is where **price** lives — the same product offered in different
    rounds has different CampaignProduct rows (and therefore different prices).
    ``organization_id`` is denormalized from the round/product (same tenant)
    so the repository can scope directly. ``sale_round_id`` and ``product_id``
    are immutable; ``price`` and ``deposit`` are editable.
    """

    def __init__(
        self,
        *,
        id_: CampaignProductId,
        organization_id: OrganizationId,
        sale_round_id: SaleRoundId,
        product_id: ProductId,
        price: Money,
        deposit: Money,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        super().__init__(id_=id_)
        now = datetime.now(UTC)
        self._organization_id = organization_id
        self._sale_round_id = sale_round_id
        self._product_id = product_id
        self._price = price
        self._deposit = deposit
        self._created_at = created_at if created_at is not None else now
        self._updated_at = updated_at if updated_at is not None else now

    @classmethod
    def create(
        cls,
        *,
        organization_id: OrganizationId,
        sale_round_id: SaleRoundId,
        product_id: ProductId,
        price: Money,
        deposit: Money,
    ) -> Self:
        """Factory: create a new campaign product with a generated id."""
        return cls(
            id_=CampaignProductId.generate(),
            organization_id=organization_id,
            sale_round_id=sale_round_id,
            product_id=product_id,
            price=price,
            deposit=deposit,
        )

    @property
    def organization_id(self) -> OrganizationId:
        return self._organization_id

    @property
    def sale_round_id(self) -> SaleRoundId:
        return self._sale_round_id

    @property
    def product_id(self) -> ProductId:
        return self._product_id

    @property
    def price(self) -> Money:
        return self._price

    @property
    def deposit(self) -> Money:
        return self._deposit

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        return self._updated_at

    def change_price(self, new_price: Money) -> None:
        """Replace the price. No-op if unchanged."""
        if new_price == self._price:
            return
        self._price = new_price
        self._touch()

    def change_deposit(self, new_deposit: Money) -> None:
        """Replace the deposit. No-op if unchanged."""
        if new_deposit == self._deposit:
            return
        self._deposit = new_deposit
        self._touch()

    def _touch(self) -> None:
        """Refresh updated_at to reflect a mutation."""
        self._updated_at = datetime.now(UTC)
