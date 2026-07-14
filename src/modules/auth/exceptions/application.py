class ApplicationError(Exception):
    """Base application error"""

    pass


class DeviceMismatchError(Exception):
    """Raised when the current device does not match the session device."""

    pass


class InvalidEmailOrPassword(ApplicationError):
    """Raised when email/password combination is invalid"""

    pass


class PermissionDenied(ApplicationError):
    """Raised when user lacks permission to perform the requested action"""

    pass


class InvalidVerificationToken(ApplicationError):
    """Raised when a verification token is invalid, expired, or has already been used."""

    pass


class BlockEmail(ApplicationError):
    """Raised when user try to use a blocked email to signup"""

    pass
