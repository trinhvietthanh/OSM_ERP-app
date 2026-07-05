from src.modules.campaign.application.dto.campaign_product import (
    CampaignProductRead,
    CreateCampaignProductInput,
)
from src.modules.campaign.application.exceptions import (
    CampaignProductAlreadyExistsError,
    SaleRoundNotFoundError,
)
from src.modules.campaign.domain.entities.campaign_product import CampaignProduct
from src.modules.campaign.domain.repository import (
    AbstractCampaignProductRepository,
    AbstractSaleRoundRepository,
)
from src.modules.campaign.domain.value_objects.campaign_product import Money
from src.modules.campaign.domain.value_objects.sale_round import SaleRoundId
from src.modules.catalog.application.exceptions import ProductNotFoundError
from src.modules.catalog.domain.repository import AbstractProductRepository
from src.modules.catalog.domain.value_objects.product import ProductId
from src.modules.organization.domain.value_objects.organization import OrganizationId


class CreateCampaignProduct:
    """Offer a product in a sale round at a round-specific price + deposit.

    Verifies the round and the product both belong to the caller's tenant, and
    that the product is not already offered in that round.
    """

    def __init__(
        self,
        campaign_products: AbstractCampaignProductRepository,
        sale_rounds: AbstractSaleRoundRepository,
        products: AbstractProductRepository,
    ) -> None:
        self._campaign_products = campaign_products
        self._sale_rounds = sale_rounds
        self._products = products

    async def execute(
        self,
        organization_id: OrganizationId,
        sale_round_id: SaleRoundId,
        inp: CreateCampaignProductInput,
    ) -> CampaignProductRead:
        if await self._sale_rounds.get(organization_id, sale_round_id) is None:
            raise SaleRoundNotFoundError(sale_round_id)
        product_id = ProductId(value=inp.product_id)
        if await self._products.get(organization_id, product_id) is None:
            raise ProductNotFoundError(product_id)
        if (
            await self._campaign_products.get_by_round_and_product(
                organization_id, sale_round_id, product_id
            )
            is not None
        ):
            raise CampaignProductAlreadyExistsError

        campaign_product = await self._campaign_products.add(
            CampaignProduct.create(
                organization_id=organization_id,
                sale_round_id=sale_round_id,
                product_id=product_id,
                price=Money(amount=inp.price),
                deposit=Money(amount=inp.deposit),
            )
        )
        return CampaignProductRead.from_entity(campaign_product)
