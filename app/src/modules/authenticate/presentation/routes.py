from fastapi import APIRouter, Depends

from src.modules.authenticate.application.commands.login import Login
from src.modules.authenticate.application.dto.auth import (
    LoginInput,
    TokenRead,
    UserRead,
)
from src.modules.authenticate.domain.entities.user import User
from src.modules.authenticate.presentation.dependencies import (
    get_current_user,
    get_login_use_case,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenRead)
async def login(
    inp: LoginInput,
    use_case: Login = Depends(get_login_use_case),
) -> TokenRead:
    """Exchange credentials for a JWT access token."""
    return await use_case.execute(inp)


@router.get("/me", response_model=UserRead)
async def me(current_user: User = Depends(get_current_user)) -> UserRead:
    """Return the currently authenticated user."""
    return UserRead.from_entity(current_user)
