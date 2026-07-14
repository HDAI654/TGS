from src.modules.core.base_vo import BaseVO
from src.modules.channels.exceptions import InvalidLanguageError


class Language(BaseVO[str]):
    def __init__(self, value: str):
        if not isinstance(value, str):
            raise InvalidLanguageError(
                f"Language must be string, got {type(value).__name__}"
            )
        value = value.strip()
        if not value:
            raise InvalidLanguageError(f"Language must be a non-empty string")
        value = value.lower()

        super().__init__(value)
