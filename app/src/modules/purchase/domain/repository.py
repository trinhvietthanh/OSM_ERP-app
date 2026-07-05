import abc
from collections.abc import Sequence

from src.modules.customer.domain.value_objects.customer import CustomerId
from src.modules.organization.domain.value_objects.organization import OrganizationId
from src.modules.purchase.domain.entities.order import Order
from src.modules.purchase.domain.value_objects.order import (
    OrderId,
    OrderStatus,
    TrackingCode,
)
from src.modules.trip.domain.value_objects.trip import TripId


class AbstractOrderRepository(abc.ABC):
    """Port for persisting Order aggregates (with lines and receipts),
    scoped to a tenant."""

    @abc.abstractmethod
    async def add(self, order: Order) -> Order:
        """Insert a new order (with children) and return the persisted aggregate.

        :raises sqlalchemy.exc.IntegrityError: on tracking-code collision —
            the caller retries with a fresh code.
        """
        ...

    @abc.abstractmethod
    async def get(self, organization_id: OrganizationId, id_: OrderId) -> Order | None:
        """Return the tenant's order with *id_* (lines + receipts loaded)."""
        ...

    @abc.abstractmethod
    async def get_by_tracking_code(self, code: TrackingCode) -> Order | None:
        """Return the order with *code* (global lookup — no tenant filter;
        the public tracking page has no org context)."""
        ...

    @abc.abstractmethod
    async def list(
        self,
        organization_id: OrganizationId,
        status: OrderStatus | None = None,
        customer_id: CustomerId | None = None,
        trip_id: TripId | None = None,
        unassigned: bool = False,
    ) -> Sequence[Order]:
        """Return the tenant's orders, newest first.

        ``unassigned=True`` filters to consolidation candidates:
        ``trip_id IS NULL`` and not "giao riêng".
        """
        ...

    @abc.abstractmethod
    async def save(self, order: Order) -> Order | None:
        """Persist changes (reconciling lines/receipts); ``None`` if not found."""
        ...
