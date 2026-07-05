from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.organization.domain.entities.organization import Organization
from src.modules.organization.domain.repository import AbstractOrganizationRepository
from src.modules.organization.domain.value_objects.organization import (
    OrganizationId,
    OrganizationName,
)
from src.modules.organization.infrastructure.mappers import (
    apply_entity_to_model,
    entity_to_model,
    model_to_entity,
)
from src.modules.organization.infrastructure.models import OrganizationModel


class SqlAlchemyOrganizationRepository(AbstractOrganizationRepository):
    """Async SQLAlchemy implementation of the Organization repository.

    The repository never commits; the caller owns the transaction
    (``await session.commit()`` / ``await session.rollback()``).
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, organization: Organization) -> Organization:
        model = entity_to_model(organization)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model, attribute_names=["created_at", "updated_at"])
        return model_to_entity(model)

    async def get(self, id_: OrganizationId) -> Organization | None:
        model = await self._session.get(OrganizationModel, id_.value)
        return model_to_entity(model) if model is not None else None

    async def get_by_name(self, name: OrganizationName) -> Organization | None:
        stmt = select(OrganizationModel).where(OrganizationModel.name == name.value)
        model = (await self._session.scalars(stmt)).one_or_none()
        return model_to_entity(model) if model is not None else None

    async def list(self) -> Sequence[Organization]:
        stmt = select(OrganizationModel).order_by(OrganizationModel.name)
        models = (await self._session.scalars(stmt)).all()
        return [model_to_entity(m) for m in models]

    async def save(self, organization: Organization) -> Organization | None:
        model = await self._session.get(OrganizationModel, organization.id_.value)
        if model is None:
            return None
        apply_entity_to_model(organization, model)
        await self._session.flush()
        await self._session.refresh(model)
        return model_to_entity(model)
