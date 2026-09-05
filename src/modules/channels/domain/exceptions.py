class DomainError(Exception):
    """Base domain error"""

    pass

# ===== VO Exceptions =====
class InvalidIDError(DomainError):
    """Raised when a ID value is invalid or malformed."""

    pass

class InvalidNameError(DomainError):
    """Raised when a Name value is invalid or malformed."""

    pass