from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.modules.customer.domain.value_objects.customer import CustomerId
from src.modules.organization.domain.value_objects.organization import OrganizationId
from src.modules.purchase.domain.entities.order import Order
from src.modules.purchase.domain.repository import AbstractOrderRepository
from src.modules.purchase.domain.value_objects.order import (
    OrderId,
    OrderStatus,
    TrackingCode,
)
from src.modules.purchase.infrastructure.mappers import (
    apply_order_to_model,
    order_entity_to_model,
    order_model_to_entity,
)
from src.modules.purchase.infrastructure.models import OrderModel
from src.modules.trip.domain.value_objects.trip import TripId


def _with_children(stmt):  # noqa: ANN001, ANN202 — SQLAlchemy Select generics
    return stmt.options(
        selectinload(OrderModel.lines), selectinload(OrderModel.receipts)
    )


class SqlAlchemyOrderRepository(AbstractOrderRepository):
    """Async SQLAlchemy implementation of the Order repository.

    Loads the whole aggregate (lines + receipts) with ``selectinload``.
    Tenant-aware except ``get_by_tracking_code`` (global public lookup).
    The repository never commits; the caller owns the transaction.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, order: Order) -> Order:
        model = order_entity_to_model(order)
        self._session.add(model)
        await self._session.flush()
        return await self._reload(model.id)

    async def get(self, organization_id: OrganizationId, id_: OrderId) -> Order | None:
        stmt = _with_children(
            select(OrderModel).where(
                OrderModel.id == id_.value,
                OrderModel.organization_id == organization_id.value,
            )
        )
        model = (await self._session.scalars(stmt)).one_or_none()
        return order_model_to_entity(model) if model is not None else None

    async def get_by_tracking_code(self, code: TrackingCode) -> Order | None:
        stmt = _with_children(
            select(OrderModel).where(OrderModel.tracking_code == code.value)
        )
        model = (await self._session.scalars(stmt)).one_or_none()
        return order_model_to_entity(model) if model is not None else None

    async def list(
        self,
        organization_id: OrganizationId,
        status: OrderStatus | None = None,
        customer_id: CustomerId | None = None,
        trip_id: TripId | None = None,
        unassigned: bool = False,
    ) -> Sequence[Order]:
        stmt = select(OrderModel).where(
            OrderModel.organization_id == organization_id.value
        )
        if status is not None:
            stmt = stmt.where(OrderModel.status == status)
        if customer_id is not None:
            stmt = stmt.where(OrderModel.customer_id == customer_id.value)
        if trip_id is not None:
            stmt = stmt.where(OrderModel.trip_id == trip_id.value)
        if unassigned:
            stmt = stmt.where(
                OrderModel.trip_id.is_(None),
                OrderModel.is_separate.is_(False),
            )
        stmt = _with_children(stmt.order_by(OrderModel.created_at.desc()))
        models = (await self._session.scalars(stmt)).all()
        return [order_model_to_entity(m) for m in models]

    async def save(self, order: Order) -> Order | None:
        stmt = _with_children(
            select(OrderModel).where(
                OrderModel.id == order.id_.value,
                OrderModel.organization_id == order.organization_id.value,
            )
        )
        model = (await self._session.scalars(stmt)).one_or_none()
        if model is None:
            return None
        apply_order_to_model(order, model)
        await self._session.flush()
        return await self._reload(model.id)

    async def _reload(self, order_id) -> Order:  # noqa: ANN001 — uuid.UUID
        """Re-select with children after a flush so timestamps and collections
        reflect DB state (refresh() does not populate selectinload rels)."""
        stmt = _with_children(select(OrderModel).where(OrderModel.id == order_id))
        model = (await self._session.scalars(stmt)).one()
        return order_model_to_entity(model)
