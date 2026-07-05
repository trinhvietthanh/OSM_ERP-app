from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.authenticate.domain.entities.user import User
from src.modules.authenticate.domain.repository import AbstractUserRepository
from src.modules.authenticate.domain.value_objects.user import Email, UserId
from src.modules.authenticate.infrastructure.mappers import model_to_entity
from src.modules.authenticate.infrastructure.models import UserModel


class SqlAlchemyUserRepository(AbstractUserRepository):
    """Async SQLAlchemy implementation of the User repository.

    The repository never commits; the caller owns the transaction
    (``await session.commit()`` / ``await session.rollback()``).
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get(self, id_: UserId) -> User | None:
        model = await self._session.get(UserModel, id_.value)
        return model_to_entity(model) if model is not None else None

    async def get_by_email(self, email: Email) -> User | None:
        # ``email.value`` is lowercased by the VO, matching how rows are stored.
        stmt = select(UserModel).where(UserModel.email == email.value)
        model = (await self._session.scalars(stmt)).one_or_none()
        return model_to_entity(model) if model is not None else None
