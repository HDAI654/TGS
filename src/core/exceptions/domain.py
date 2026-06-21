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
