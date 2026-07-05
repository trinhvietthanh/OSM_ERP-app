from src.modules.customer.application.dto.customer import (
    CreateCustomerInput,
    CustomerRead,
)
from src.modules.customer.domain.entities.customer import Customer
from src.modules.customer.domain.repository import AbstractCustomerRepository
from src.modules.customer.domain.value_objects.customer import (
    CustomerName,
    PhoneNumber,
)
from src.modules.organization.domain.value_objects.organization import OrganizationId


class CreateCustomer:
    """Create a new customer in the caller's tenant."""

    def __init__(self, repo: AbstractCustomerRepository) -> None:
        self._repo = repo

    async def execute(
        self, organization_id: OrganizationId, inp: CreateCustomerInput
    ) -> CustomerRead:
        customer = await self._repo.add(
            Customer.create(
                organization_id=organization_id,
                name=CustomerName(value=inp.name),
                phone=PhoneNumber(value=inp.phone) if inp.phone else None,
                note=inp.note,
            )
        )
        return CustomerRead.from_entity(customer)
