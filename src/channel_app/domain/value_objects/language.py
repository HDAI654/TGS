from src.core.base_vo import BaseVO
from src.core.exceptions import InvalidLanguageError
from src.core.conf import Config


class Language(BaseVO[str]):
    def __init__(self, value: str):
        if not isinstance(value, str):
            raise InvalidLanguageError(
                f"Language must be string, got {type(value).__name__}"
            )
        value = value.strip()
        if not value:
            raise InvalidLanguageError(f"Language must be a non-empty string")
        if value not in Config.ALLOWED_LANGUAGES:
            raise InvalidLanguageError(f"Invalid Language !")

        super().__init__(value)
