class CrawlerError(Exception):
    """Base exception for all crawler-related errors."""

    pass


class CrawlerConnectionError(CrawlerError):
    """Raised when unable to connect to the external API."""

    pass


class CrawlerTimeoutError(CrawlerError):
    """Raised when the request to external API times out."""

    pass


class CrawlerHTTPError(CrawlerError):
    """Raised when HTTP response status is not successful."""

    pass


class CrawlerParseError(CrawlerError):
    """Raised when response content cannot be parsed."""

    pass


class CrawlerEmptyResponseError(CrawlerError):
    """Raised when the response is empty."""

    pass


class CrawlerInvalidDataError(CrawlerError):
    """Raised when the parsed data is invalid or malformed."""

    pass


####################################
####################################


class DatabaseError(Exception):
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
