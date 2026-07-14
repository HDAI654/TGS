class InfrastructureError(Exception):
    """Base infrastructure error"""

    pass


# ======= DB =======
class DatabaseError(InfrastructureError):
    """Base exception for database errors"""

    pass


class DatabaseConnectionError(DatabaseError):
    """Raised when cannot connect to database"""

    pass


class DatabaseTimeoutError(DatabaseError):
    """Raised when database operation times out"""

    pass


class DatabaseOperationError(DatabaseError):
    """Raised when database operation fails"""

    pass


class NoChangesError(InfrastructureError):
    """No changes provided for update"""

    pass


class InvalidFieldError(InfrastructureError):
    """Invalid field provided for update"""

    pass


# ======= Cache =======
class CacheError(Exception):
    """Base exception for all cache infrastructure failures"""

    pass


class CacheConnectionError(CacheError):
    """Raised when cannot connect to cache"""

    pass


class CacheTimeoutError(CacheError):
    """Raised when cache operation times out"""

    pass


class CacheOperationError(CacheError):
    """Raised when cache operation fails"""

    pass


# ======= Auth Token =======
class InvalidAuthTokenError(InfrastructureError):
    """Raised when an authentication token is invalid or malformed."""

    pass
