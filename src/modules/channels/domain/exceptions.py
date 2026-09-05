class DomainError(Exception):
    """Base domain error"""

    pass

# ===== Entity Exceptions =====
class ChannelException(DomainError):
    """Base Channel error"""

    pass


class ChannelNotFoundError(ChannelException):
    """Raised when Channel not found"""

    pass

class CountryException(DomainError):
    """Base Country error"""

    pass


class CountryNotFoundError(CountryException):
    """Country not found"""

    pass

