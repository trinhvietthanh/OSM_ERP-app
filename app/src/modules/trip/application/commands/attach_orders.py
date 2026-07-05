from src.modules.organization.domain.value_objects.organization import OrganizationId
from src.modules.purchase.application.exceptions import OrderNotFoundError
from src.modules.purchase.domain.repository import AbstractOrderRepository
from src.modules.purchase.domain.value_objects.order import OrderId
from src.modules.trip.application.dto.trip import AttachOrdersInput
from src.modules.trip.application.exceptions import (
    OrderNotAttachableError,
    TripNotFoundError,
)
from src.modules.trip.domain.repository import AbstractTripRepository
from src.modules.trip.domain.value_objects.trip import TripId
from src.shared.domain.base import DomainError


class AttachOrders:
    """Attach orders to a trip (gom đơn). Trip must still be PLANNING."""

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
        trip_id: TripId,
        inp: AttachOrdersInput,
    ) -> None:
        trip = await self._trips.get(organization_id, trip_id)
        if trip is None:
            raise TripNotFoundError(trip_id.value)
        if not trip.is_planning:
            raise OrderNotAttachableError(
                "Orders can only be attached while the trip is planning."
            )

        for raw_id in inp.order_ids:
            order_id = OrderId(value=raw_id)
            order = await self._orders.get(organization_id, order_id)
            if order is None:
                raise OrderNotFoundError(raw_id)
            try:
                order.attach_to_trip(trip_id)
            except DomainError as exc:
                raise OrderNotAttachableError(
                    f"Order {order.tracking_code.value}: {exc}"
                ) from exc
            await self._orders.save(order)


class DetachOrder:
    """Detach one order from a trip. Trip must still be PLANNING."""

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
        trip_id: TripId,
        order_id: OrderId,
    ) -> None:
        trip = await self._trips.get(organization_id, trip_id)
        if trip is None:
            raise TripNotFoundError(trip_id.value)
        if not trip.is_planning:
            raise OrderNotAttachableError(
                "Orders can only be detached while the trip is planning."
            )

        order = await self._orders.get(organization_id, order_id)
        if order is None or order.trip_id != trip_id:
            raise OrderNotFoundError(order_id.value)
        order.detach_from_trip()
        await self._orders.save(order)
