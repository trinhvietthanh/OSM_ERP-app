from src.modules.customer.application.dto.customer import CustomerRead
from src.modules.customer.domain.repository import AbstractCustomerRepository
from src.modules.customer.domain.value_objects.customer import CustomerId
from src.modules.organization.domain.value_objects.organization import OrganizationId


class GetCustomer:
    """Fetch a single customer in the caller's tenant."""

    def __init__(self, repo: AbstractCustomerRepository) -> None:
        self._repo = repo

    async def execute(
        self, organization_id: OrganizationId, id_: CustomerId
    ) -> CustomerRead | None:
        customer = await self._repo.get(organization_id, id_)
        return CustomerRead.from_entity(customer) if customer is not None else None
