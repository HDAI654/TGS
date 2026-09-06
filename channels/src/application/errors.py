class ApplicationError(Exception):
    """Base error for expected application-layer failures."""


class InvalidPaginationError(ApplicationError):
    """Raised when pagination arguments are outside the supported range."""
