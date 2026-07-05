from src.modules.customer.application.dto.customer import (
    CustomerRead,
    UpdateCustomerInput,
)
from src.modules.customer.application.exceptions import CustomerNotFoundError
from src.modules.customer.domain.repository import AbstractCustomerRepository
from src.modules.customer.domain.value_objects.customer import (
    CustomerId,
    CustomerName,
    PhoneNumber,
)
from src.modules.organization.domain.value_objects.organization import OrganizationId


class UpdateCustomer:
    """Apply a partial update to an existing customer."""

    def __init__(self, repo: AbstractCustomerRepository) -> None:
        self._repo = repo

    async def execute(
        self,
        organization_id: OrganizationId,
        id_: CustomerId,
        inp: UpdateCustomerInput,
    ) -> CustomerRead:
        customer = await self._repo.get(organization_id, id_)
        if customer is None:
            raise CustomerNotFoundError(id_.value)

        if inp.name is not None:
            customer.rename(CustomerName(value=inp.name))
        if inp.phone is not None:
            # Empty string clears the phone; non-empty replaces it.
            customer.change_phone(PhoneNumber(value=inp.phone) if inp.phone else None)
        if inp.note is not None:
            customer.change_note(inp.note)
        if inp.active is not None:
            if inp.active:
                customer.activate()
            else:
                customer.deactivate()

        saved = await self._repo.save(customer)
        if saved is None:
            raise CustomerNotFoundError(id_.value)
        return CustomerRead.from_entity(saved)
