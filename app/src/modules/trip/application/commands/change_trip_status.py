from src.modules.organization.domain.value_objects.organization import OrganizationId
from src.modules.purchase.domain.repository import AbstractOrderRepository
from src.modules.purchase.domain.value_objects.order import OrderStatus
from src.modules.trip.application.dto.trip import ChangeTripStatusInput, TripRead
from src.modules.trip.application.exceptions import TripNotFoundError
from src.modules.trip.domain.repository import AbstractTripRepository
from src.modules.trip.domain.value_objects.trip import TripId, TripStatus
from src.shared.domain.base import DomainError


class ChangeTripStatus:
    """Advance a trip through its lifecycle and cascade to its orders.

    Same unit of work (session) as the order updates, so the whole change
    commits atomically:
    - trip → BUYING: attached orders move to PURCHASING;
    - trip → ARRIVED: attached PURCHASING/PURCHASED orders move to ARRIVED.
    Other trip transitions leave orders untouched.
    """

    def __init__(
        self,
        trips: AbstractTripRepository,
        orders: AbstractOrderRepository,
    ) -> None:
        self._trips = trips
        self._orders = orders

    async def execute(
        self,
        organization_id: OrganizationId,
        id_: TripId,
        inp: ChangeTripStatusInput,
    ) -> TripRead:
        try:
            new_status = TripStatus(inp.status)
        except ValueError as exc:
            raise DomainError(f"Unknown trip status: {inp.status!r}.") from exc

        trip = await self._trips.get(organization_id, id_)
        if trip is None:
            raise TripNotFoundError(id_.value)

        trip.change_status(new_status)

        if new_status is TripStatus.BUYING:
            await self._cascade(
                organization_id,
                id_,
                from_statuses=(OrderStatus.PENDING, OrderStatus.CONFIRMED),
                to_status=OrderStatus.PURCHASING,
            )
        elif new_status is TripStatus.ARRIVED:
            await self._cascade(
                organization_id,
                id_,
                from_statuses=(OrderStatus.PURCHASING, OrderStatus.PURCHASED),
                to_status=OrderStatus.ARRIVED,
            )

        saved = await self._trips.save(trip)
        if saved is None:
            raise TripNotFoundError(id_.value)
        return TripRead.from_entity(saved)

    async def _cascade(
        self,
        organization_id: OrganizationId,
        trip_id: TripId,
        from_statuses: tuple[OrderStatus, ...],
        to_status: OrderStatus,
    ) -> None:
        for order in await self._orders.list(organization_id, trip_id=trip_id):
            if order.status in from_statuses:
                # PENDING orders hop through CONFIRMED so every step stays a
                # legal transition (pending → purchasing is not allowed).
                if (
                    order.status is OrderStatus.PENDING
                    and to_status is OrderStatus.PURCHASING
                ):
                    order.change_status(OrderStatus.CONFIRMED)
                if (
                    order.status is OrderStatus.PURCHASING
                    and to_status is OrderStatus.ARRIVED
                ):
                    order.change_status(OrderStatus.PURCHASED)
                order.change_status(to_status)
                await self._orders.save(order)
