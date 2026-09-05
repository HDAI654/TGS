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

class InvalidCountryCodeError(DomainError):
    """Raised when a Country code value is invalid or malformed."""

    pass

class InvalidCountError(DomainError):
    """Raised when a Count value is invalid or malformed."""

    pass


class InvalidHasChannelsError(DomainError):
    """Raised when a HasChannel value is invalid or malformed."""

    pass


# ===== Entity Exceptions =====
class ChannelException(DomainError):
    """Base Channel error"""

    pass


class ChannelNotFoundError(ChannelException):
    """Raised when Channel not found"""

    pass
