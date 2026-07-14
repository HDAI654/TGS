class DomainError(Exception):
    """Base domain error"""

    pass


# ===== VO Exceptions =====
class InvalidIDError(DomainError):
    """Raised when a ID value is invalid or malformed."""

    pass


class InvalidIsGeoBlockedError(DomainError):
    """Raised when a IsGeoBlocked value is invalid or malformed."""

    pass


class InvalidNameError(DomainError):
    """Raised when a Name value is invalid or malformed."""

    pass


class InvalidURLError(DomainError):
    """Raised when a URL value is invalid or malformed."""

    pass


class InvalidLanguageError(DomainError):
    """Raised when a Language value is invalid or malformed."""

    pass


class InvalidCountryCodeError(DomainError):
    """Raised when a Country code value is invalid or malformed."""

    pass


class InvalidTimezoneError(DomainError):
    """Raised when a Timezone value is invalid or malformed."""

    pass


class InvalidCountError(DomainError):
    """Raised when a Count value is invalid or malformed."""

    pass


class InvalidHasChannelsError(DomainError):
    """Raised when a HasChannel value is invalid or malformed."""

    pass


class InvalidCategoryError(DomainError):
    """Raised when a Category value is invalid or malformed."""

    pass


class InvalidDateError(DomainError):
    """Raised when a Date value is invalid or malformed."""

    pass


# ===== Entity Exceptions =====
# Channel
class ChannelException(DomainError):
    """Base Channel error"""

    pass


class ChannelNotFoundError(ChannelException):
    """Channel not found"""

    pass


class ChannelDuplicateError(ChannelException):
    """Channel with same unique field exists"""

    pass


# Country
class CountryException(DomainError):
    """Base Country error"""

    pass


class CountryNotFoundError(CountryException):
    """Country not found"""

    pass


class CountryDuplicateError(CountryException):
    """Country with same unique field exists"""

    pass


# URL
class URLException(DomainError):
    """Base URL error"""

    pass


class URLNotFoundError(URLException):
    """URL not found"""

    pass


class URLDuplicateError(URLException):
    """URL with same unique field exists"""

    pass
