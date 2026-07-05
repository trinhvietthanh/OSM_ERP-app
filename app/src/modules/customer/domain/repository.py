import abc
from collections.abc import Sequence

from src.modules.customer.domain.entities.customer import Customer
from src.modules.customer.domain.value_objects.customer import CustomerId
from src.modules.organization.domain.value_objects.organization import OrganizationId


class AbstractCustomerRepository(abc.ABC):
    """Port for persisting Customer aggregates, scoped to a tenant."""

    @abc.abstractmethod
    async def add(self, customer: Customer) -> Customer:
        """Insert a new customer and return the persisted aggregate."""
        ...

    @abc.abstractmethod
    async def get(
        self, organization_id: OrganizationId, id_: CustomerId
    ) -> Customer | None:
        """Return the tenant's customer with *id_*, or ``None``."""
        ...

    @abc.abstractmethod
    async def list(
        self,
        organization_id: OrganizationId,
        search: str | None = None,
        active_only: bool = True,
    ) -> Sequence[Customer]:
        """Return the tenant's customers, filtered by *search* (name/phone)."""
        ...

    @abc.abstractmethod
    async def save(self, customer: Customer) -> Customer | None:
        """Persist changes to an existing customer; ``None`` if not found."""
        ...
