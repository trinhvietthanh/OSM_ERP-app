from src.modules.authenticate.application.dto.auth import LoginInput, TokenRead
from src.modules.authenticate.application.exceptions import InvalidCredentialsError
from src.modules.authenticate.domain.repository import AbstractUserRepository
from src.modules.authenticate.domain.services import (
    AbstractPasswordHasher,
    AbstractTokenService,
)
from src.modules.authenticate.domain.value_objects.user import Email
from src.modules.organization.domain.repository import AbstractOrganizationRepository
from src.modules.organization.domain.value_objects.organization import OrganizationStatus


class Login:
    """Authenticate a user and issue a JWT access token.

    Every failure path raises the same :class:`InvalidCredentialsError` so the
    caller cannot tell which check failed. The user's organization (tenant) is
    read — never written — to confirm it exists and is active before a token is
    issued; a suspended or missing tenant blocks login.
    """

    def __init__(
        self,
        users: AbstractUserRepository,
        organizations: AbstractOrganizationRepository,
        hasher: AbstractPasswordHasher,
        token_service: AbstractTokenService,
    ) -> None:
        self._users = users
        self._organizations = organizations
        self._hasher = hasher
        self._token_service = token_service

    async def execute(self, inp: LoginInput) -> TokenRead:
        user = await self._users.get_by_email(Email.from_string(inp.email))
        if user is None or not user.is_active:
            raise InvalidCredentialsError
        if not self._hasher.verify(inp.password, user.password_hash.value):
            raise InvalidCredentialsError

        organization = await self._organizations.get(user.organization_id)
        if (
            organization is None
            or organization.status is OrganizationStatus.SUSPENDED
        ):
            raise InvalidCredentialsError

        token = self._token_service.create_access_token(user)
        return TokenRead(
            access_token=token,
            expires_in=self._token_service.access_ttl_seconds,
        )
