class DomainError(Exception):
    """Base domain error"""

    pass


# ===== VO Exceptions =====
class InvalidIDError(DomainError):
    pass


class InvalidIsGeoBlockedError(DomainError):
    pass


class InvalidNameError(DomainError):
    pass


class InvalidURLError(DomainError):
    pass


class InvalidLanguageError(DomainError):
    pass


class InvalidCountryCodeError(DomainError):
    pass


class InvalidTimezoneError(DomainError):
    pass


class InvalidCountError(DomainError):
    pass


class InvalidHasChannelsError(DomainError):
    pass
