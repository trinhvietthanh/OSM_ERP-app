from fastapi import Depends, Header, HTTPException, status
from jwt.exceptions import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.postgres.session import get_session
from src.modules.authenticate.application.commands.login import Login
from src.modules.authenticate.domain.entities.user import User
from src.modules.authenticate.domain.repository import AbstractUserRepository
from src.modules.authenticate.domain.services import (
    AbstractPasswordHasher,
    AbstractTokenService,
)
from src.modules.authenticate.domain.value_objects.user import UserId
from src.modules.authenticate.infrastructure.jwt_token_service import JwtTokenService
from src.modules.authenticate.infrastructure.password_hasher import BcryptPasswordHasher
from src.modules.authenticate.infrastructure.repository import SqlAlchemyUserRepository
from src.modules.authenticate.infrastructure.settings import get_jwt_settings
from src.modules.organization.domain.repository import AbstractOrganizationRepository
from src.modules.organization.infrastructure.repository import (
    SqlAlchemyOrganizationRepository,
)
from src.shared.domain.base import DomainError


def _credentials_error() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_user_repository(
    session: AsyncSession = Depends(get_session),
) -> AbstractUserRepository:
    return SqlAlchemyUserRepository(session)


def get_organization_repository(
    session: AsyncSession = Depends(get_session),
) -> AbstractOrganizationRepository:
    return SqlAlchemyOrganizationRepository(session)


def get_password_hasher() -> AbstractPasswordHasher:
    return BcryptPasswordHasher()


def get_token_service() -> AbstractTokenService:
    return JwtTokenService(get_jwt_settings())


def get_login_use_case(
    users: AbstractUserRepository = Depends(get_user_repository),
    organizations: AbstractOrganizationRepository = Depends(get_organization_repository),
    hasher: AbstractPasswordHasher = Depends(get_password_hasher),
    token_service: AbstractTokenService = Depends(get_token_service),
) -> Login:
    return Login(users, organizations, hasher, token_service)


async def get_current_user(
    authorization: str | None = Header(None),
    token_service: AbstractTokenService = Depends(get_token_service),
    users: AbstractUserRepository = Depends(get_user_repository),
) -> User:
    """Resolve the ``Authorization: Bearer <token>`` header to the current user.

    :raises HTTPException: 401 if the header is missing/malformed, the token is
        invalid/expired, or the user no longer exists / is inactive.
    """
    error = _credentials_error()
    if not authorization:
        raise error
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise error
    try:
        claims = token_service.decode(token)
    except InvalidTokenError:
        raise error from None
    if claims.get("type") != "access" or not claims.get("sub"):
        raise error
    try:
        user_id = UserId.from_string(str(claims["sub"]))
    except DomainError:
        raise error from None
    user = await users.get(user_id)
    if user is None or not user.is_active:
        raise error
    return user
