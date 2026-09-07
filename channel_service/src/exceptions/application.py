class ApplicationError(Exception):
    """Base application error."""


class InvalidPaginationError(ApplicationError):
    """Raised when limit or offset violates the query contract."""
