from src.shared.domain.base import DomainError


class InvalidCredentialsError(DomainError):
    """Raised when login fails for any reason.

    Deliberately generic — unknown user, wrong password, inactive user, or an
    inactive/missing tenant all surface as the same error so a caller cannot
    tell which check failed.
    """

    def __init__(self) -> None:
        super().__init__("Invalid credentials.")
