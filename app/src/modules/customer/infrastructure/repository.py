from collections.abc import Sequence

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.customer.domain.entities.customer import Customer
from src.modules.customer.domain.repository import AbstractCustomerRepository
from src.modules.customer.domain.value_objects.customer import CustomerId
from src.modules.customer.infrastructure.mappers import (
    apply_customer_to_model,
    customer_entity_to_model,
    customer_model_to_entity,
)
from src.modules.customer.infrastructure.models import CustomerModel
from src.modules.organization.domain.value_objects.organization import OrganizationId


class SqlAlchemyCustomerRepository(AbstractCustomerRepository):
    """Async SQLAlchemy implementation of the Customer repository.

    Tenant-aware: every read is qualified by ``organization_id``. The
    repository never commits; the caller owns the transaction.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, customer: Customer) -> Customer:
        model = customer_entity_to_model(customer)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model, attribute_names=["created_at", "updated_at"])
        return customer_model_to_entity(model)

    async def get(
        self, organization_id: OrganizationId, id_: CustomerId
    ) -> Customer | None:
        stmt = select(CustomerModel).where(
            CustomerModel.id == id_.value,
            CustomerModel.organization_id == organization_id.value,
        )
        model = (await self._session.scalars(stmt)).one_or_none()
        return customer_model_to_entity(model) if model is not None else None

    async def list(
        self,
        organization_id: OrganizationId,
        search: str | None = None,
        active_only: bool = True,
    ) -> Sequence[Customer]:
        stmt = select(CustomerModel).where(
            CustomerModel.organization_id == organization_id.value
        )
        if active_only:
            stmt = stmt.where(CustomerModel.active.is_(True))
        if search:
            pattern = f"%{search.strip()}%"
            stmt = stmt.where(
                or_(
                    CustomerModel.name.ilike(pattern),
                    CustomerModel.phone.ilike(pattern),
                )
            )
        stmt = stmt.order_by(CustomerModel.name)
        models = (await self._session.scalars(stmt)).all()
        return [customer_model_to_entity(m) for m in models]

    async def save(self, customer: Customer) -> Customer | None:
        stmt = select(CustomerModel).where(
            CustomerModel.id == customer.id_.value,
            CustomerModel.organization_id == customer.organization_id.value,
        )
        model = (await self._session.scalars(stmt)).one_or_none()
        if model is None:
            return None
        apply_customer_to_model(customer, model)
        await self._session.flush()
        await self._session.refresh(model)
        return customer_model_to_entity(model)
