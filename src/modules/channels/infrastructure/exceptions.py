class InfrastructureError(Exception):
    """Base infrastructure error."""


class DatabaseConnectionError(InfrastructureError):
    """Raised when a database connection fails."""


class DatabaseTimeoutError(InfrastructureError):
    """Raised when a database operation times out."""


class DatabaseOperationError(InfrastructureError):
    """Raised when a database operation fails for other reasons."""