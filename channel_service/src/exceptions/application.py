"""Application-layer errors for the channels service.

Raised by use cases for orchestration/validation conditions that are not
infrastructure failures. Presentation translates these into protocol responses.
"""


class ApplicationError(Exception):
    """Base application error."""


class InvalidPaginationError(ApplicationError):
    """Raised when limit or offset violates the query contract."""
