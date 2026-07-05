import abc

from src.modules.authenticate.domain.entities.user import User
from src.modules.authenticate.domain.value_objects.user import Email, UserId


class AbstractUserRepository(abc.ABC):
    """Port for reading User aggregates.

    The auth use cases (login, me) only read users; seeding is performed by
    infrastructure tooling directly. Implementations live in the infrastructure
    layer (e.g. :class:`SqlAlchemyUserRepository`). This interface depends only
    on domain types and never on SQLAlchemy.
    """

    @abc.abstractmethod
    async def get(self, id_: UserId) -> User | None:
        """Return the user with *id_*, or ``None`` if not found."""
        ...

    @abc.abstractmethod
    async def get_by_email(self, email: Email) -> User | None:
        """Return the user with *email* (already lowercased by the VO)."""
        ...
