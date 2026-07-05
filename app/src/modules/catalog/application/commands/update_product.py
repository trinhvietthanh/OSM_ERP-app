from src.modules.catalog.application.dto.product import (
    ProductRead,
    UpdateProductInput,
)
from src.modules.catalog.application.exceptions import ProductNotFoundError
from src.modules.catalog.domain.repository import AbstractProductRepository
from src.modules.catalog.domain.value_objects.product import (
    Description,
    ProductId,
    ProductName,
)
from src.modules.organization.domain.value_objects.organization import OrganizationId


class UpdateProduct:
    """Apply a partial update to a product in the caller's tenant.

    ``name``/``description``/``active`` are each applied only when provided;
    ``active=False`` soft-deletes, ``active=True`` reactivates. (Pricing is not
    on the product — it lives on CampaignProduct.)
    """

    def __init__(self, repo: AbstractProductRepository) -> None:
        self._repo = repo

    async def execute(
        self,
        organization_id: OrganizationId,
        id_: ProductId,
        inp: UpdateProductInput,
    ) -> ProductRead:
        product = await self._repo.get(organization_id, id_)
        if product is None:
            raise ProductNotFoundError(id_)

        if inp.name is not None:
            product.rename(ProductName(value=inp.name))
        if inp.description is not None:
            product.change_description(Description(value=inp.description))
        if inp.active is True:
            product.activate()
        elif inp.active is False:
            product.deactivate()

        updated = await self._repo.save(product)
        assert updated is not None  # existence confirmed by get() above
        return ProductRead.from_entity(updated)
