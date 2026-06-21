from src.core.base_vo import BaseVO
from src.core.exceptions import InvalidLanguageError
import pycountry

ALL_LANGUAGES_ISO_639_3 = {lang.alpha_3 for lang in pycountry.languages}

class Language(BaseVO[str]):
    ALLOWED_LANGUAGES = ALL_LANGUAGES_ISO_639_3
    def __init__(self, value: str):
        if not isinstance(value, str):
            raise InvalidLanguageError(f"Language must be string, got {type(value).__name__}")
        value = value.strip()
        if not value:
            raise InvalidLanguageError(f"Language must be a non-empty string")
        if value not in self.ALLOWED_LANGUAGES:
            raise InvalidLanguageError(f"Invalid Language !")
        
        super().__init__(value)
