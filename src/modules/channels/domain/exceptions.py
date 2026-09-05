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

class InvalidCategoryNameError(DomainError):
    """Raised when a CategoryName value is invalid or malformed."""

    pass

class InvalidLanguageError(DomainError):
    """Raised when a Language value is invalid or malformed."""

    pass