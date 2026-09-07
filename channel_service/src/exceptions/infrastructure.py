class InfrastructureError(Exception):
    """Base infrastructure error."""


class DatabaseConnectionError(InfrastructureError):
    """Database connection could not be established or was lost."""


class DatabaseTimeoutError(InfrastructureError):
    """A database operation exceeded its timeout."""


class DatabaseOperationError(InfrastructureError):
    """A database operation failed for a non-connection, non-timeout reason."""
