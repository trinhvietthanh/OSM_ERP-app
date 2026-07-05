import abc
from collections.abc import Sequence

from src.modules.campaign.domain.entities.campaign_product import CampaignProduct
from src.modules.campaign.domain.entities.sale_round import SaleRound
from src.modules.campaign.domain.value_objects.campaign_product import (
    CampaignProductId,
)
from src.modules.campaign.domain.value_objects.sale_round import (
    RoundCode,
    SaleRoundId,
)
from src.modules.catalog.domain.value_objects.product import ProductId
from src.modules.organization.domain.value_objects.organization import OrganizationId


class AbstractSaleRoundRepository(abc.ABC):
    """Port for persisting SaleRound aggregates, scoped to a tenant."""

    @abc.abstractmethod
    async def add(self, sale_round: SaleRound) -> SaleRound:
        """Insert a new round and return the persisted aggregate."""
        ...

    @abc.abstractmethod
    async def get(
        self, organization_id: OrganizationId, id_: SaleRoundId
    ) -> SaleRound | None:
        """Return the tenant's round with *id_*, or ``None``."""
        ...

    @abc.abstractmethod
    async def get_by_code(
        self, organization_id: OrganizationId, code: RoundCode
    ) -> SaleRound | None:
        """Return the tenant's round with *code*, or ``None``."""
        ...

    @abc.abstractmethod
    async def list(self, organization_id: OrganizationId) -> Sequence[SaleRound]:
        """Return the tenant's rounds, newest first."""
        ...

    @abc.abstractmethod
    async def save(self, sale_round: SaleRound) -> SaleRound | None:
        """Persist changes to an existing round; ``None`` if not found."""
        ...


class AbstractCampaignProductRepository(abc.ABC):
    """Port for persisting CampaignProduct aggregates, scoped to a tenant.

    Scoping is by ``organization_id`` (denormalized on each row) so reads
    cannot leak another tenant's offerings.
    """

    @abc.abstractmethod
    async def add(self, campaign_product: CampaignProduct) -> CampaignProduct:
        """Insert a new campaign product and return the persisted aggregate."""
        ...

    @abc.abstractmethod
    async def get(
        self, organization_id: OrganizationId, id_: CampaignProductId
    ) -> CampaignProduct | None:
        """Return the tenant's campaign product with *id_*, or ``None``."""
        ...

    @abc.abstractmethod
    async def get_by_round_and_product(
        self,
        organization_id: OrganizationId,
        sale_round_id: SaleRoundId,
        product_id: ProductId,
    ) -> CampaignProduct | None:
        """Return the offering of *product_id* in *sale_round_id*, or ``None``."""
        ...

    @abc.abstractmethod
    async def list(
        self, organization_id: OrganizationId, sale_round_id: SaleRoundId
    ) -> Sequence[CampaignProduct]:
        """Return the offerings in a round."""
        ...

    @abc.abstractmethod
    async def save(self, campaign_product: CampaignProduct) -> CampaignProduct | None:
        """Persist changes; ``None`` if not found."""
        ...
