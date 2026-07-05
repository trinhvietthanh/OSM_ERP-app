from src.modules.purchase.application.dto.tracking import TrackingRead
from src.modules.purchase.domain.repository import AbstractOrderRepository
from src.modules.purchase.domain.value_objects.order import TrackingCode


class TrackOrder:
    """Public lookup by tracking code — no tenant context, no auth.

    The 31^8 code keyspace is the access control: codes are unguessable, and
    the response carries nothing sensitive (see TrackingRead).
    """

    def __init__(self, orders: AbstractOrderRepository) -> None:
        self._orders = orders

    async def execute(self, code: TrackingCode) -> TrackingRead | None:
        order = await self._orders.get_by_tracking_code(code)
        return TrackingRead.from_entity(order) if order is not None else None
