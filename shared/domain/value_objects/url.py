from src.core.base_vo import BaseVO
from src.core.exceptions import InvalidURLError
from urllib.parse import urlparse


class URL(BaseVO[str]):
    ALLOWED_SCHEMES = {"http", "https"}

    def __init__(self, value: str):
        if not isinstance(value, str):
            raise InvalidURLError(f"URL must be string, got {type(value).__name__}")
        value = value.strip()
        if not value:
            raise InvalidURLError(f"URL must be a non-empty string")
        if len(value) > 2048:
            raise InvalidURLError(f"URL is so long !")

        parsed = urlparse(value)
        if parsed.scheme not in self.ALLOWED_SCHEMES:
            raise InvalidURLError(
                f"Invalid URL scheme: {parsed.scheme}. "
                f"Allowed: {', '.join(self.ALLOWED_SCHEMES)}"
            )

        if not parsed.hostname:
            raise InvalidURLError("URL must contain a hostname")

        if not all([parsed.scheme, parsed.netloc]):
            raise InvalidURLError("Invalid URL format")

        super().__init__(value)
