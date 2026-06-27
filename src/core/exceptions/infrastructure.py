class InfrastructureError(Exception):
    """Base infrastructure error"""

    pass


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


# ===== ChannelRepo Exceptions =====
class ChannelException(InfrastructureError):
    """Base Channel error"""

    pass


class ChannelNotFoundError(ChannelException):
    """Channel not found in database"""

    pass


class ChannelDuplicateError(ChannelException):
    """Channel with same unique field exists"""

    pass


# ===== CountryRepo Exceptions =====
class CountryException(InfrastructureError):
    """Base Country error"""

    pass


class CountryNotFoundError(CountryException):
    """Country not found in database"""

    pass


class CountryDuplicateError(CountryException):
    """Country with same unique field exists"""

    pass


# ===== ChannelRepo Exceptions =====
class URLException(InfrastructureError):
    """Base URL error"""

    pass


class URLNotFoundError(URLException):
    """URL not found in database"""

    pass


class URLDuplicateError(URLException):
    """URL with same unique field exists"""

    pass


# ===== Crawler Exceptions =====
class CrawlerException(InfrastructureError):
    """Base Crawler error"""

    pass


class ExtractTimeOutError(CrawlerException):
    """Extract operation time out"""

    pass


class CountryChannelsNotFoundError(CrawlerException):
    """Crawler couldn't find the country to get its channels"""

    pass
