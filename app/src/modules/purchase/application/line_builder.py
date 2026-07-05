from src.modules.catalog.application.exceptions import ProductNotFoundError
from src.modules.catalog.domain.repository import AbstractProductRepository
from src.modules.catalog.domain.value_objects.product import ProductId
from src.modules.organization.domain.value_objects.organization import OrganizationId
from src.modules.purchase.application.dto.order import OrderLineInput
from src.modules.purchase.domain.entities.order import OrderLine
from src.modules.purchase.domain.value_objects.order import Quantity
from src.shared.domain.base import DomainError
from src.shared.domain.money import Money


async def build_lines(
    products: AbstractProductRepository,
    organization_id: OrganizationId,
    inputs: list[OrderLineInput],
) -> list[OrderLine]:
    """Turn line inputs into OrderLine entities, snapshotting product
    code/name and validating each product belongs to the tenant.

    :raises ProductNotFoundError: if a product id is not in the tenant.
    :raises DomainError: if the input list is empty or values are invalid.
    """
    if not inputs:
        raise DomainError("An order must have at least one line.")
    lines: list[OrderLine] = []
    for inp in inputs:
        product = await products.get(organization_id, ProductId(value=inp.product_id))
        if product is None:
            raise ProductNotFoundError(inp.product_id)
        lines.append(
            OrderLine.create(
                product_id=product.id_,
                product_code=product.code.value,
                product_name=product.name.value,
                quantity=Quantity(value=inp.quantity),
                unit_price=Money(amount=inp.unit_price),
                unit_deposit=Money(amount=inp.unit_deposit),
            )
        )
    return lines
