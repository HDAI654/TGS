class DomainError(Exception):
    """Base domain error"""

    pass


# ======= VOs =======
class InvalidDateError(DomainError):
    """Raised when a Date value is invalid or malformed."""

    pass


class InvalidDeviceError(DomainError):
    """Raised when a Device value is invalid or malformed."""

    pass


class InvalidEmailVerificationTokenError(DomainError):
    """Raised when a EmailVerificationToken value is invalid or malformed."""

    pass


class InvalidEmailError(DomainError):
    """Raised when a Email value is invalid or malformed."""

    pass


class InvalidHashedPasswordError(DomainError):
    """Raised when a HashedPassword value is invalid or malformed."""

    pass


class InvalidPasswordError(DomainError):
    """Raised when a Password value is invalid or malformed."""

    pass


class WeakPasswordError(DomainError):
    """Raised when a Password does not meet strength requirements."""

    pass


class InvalidSessionIDError(DomainError):
    """Raised when a SessionID value is invalid or malformed."""

    pass


class InvalidUserIDError(DomainError):
    """Raised when a UserID value is invalid or malformed."""

    pass


# ======= # User Exceptions =======
class UserException(DomainError):
    """Base User error"""

    pass


class UserNotFoundError(UserException):
    """User not found"""

    pass


class UserDuplicateError(UserException):
    """User with same unique field exists"""

    pass


# ======= # Session Exceptions =======
class SessionException(DomainError):
    """Base Session error"""

    pass


class SessionNotFoundError(SessionException):
    """Session not found"""

    def __init__(self, *args, context: str = None):
        super().__init__(*args)
        self.context = context


class SessionDuplicateError(SessionException):
    """Session with same unique field exists"""

    pass
