import pytest
from shared.domain.value_objects.language import Language
from src.core.exceptions import InvalidLanguageError


class TestLanguage:
    def test_not_str_Language(self):
        with pytest.raises(InvalidLanguageError):
            Language(25)
            Language(None)

    def test_empty_str_Language(self):
        with pytest.raises(InvalidLanguageError):
            Language("")
            Language(" ")
            Language("  ")

    def test_Language_strip(self):
        str_Language = "        eng  "
        language = Language(str_Language)

        assert language.value == str_Language.strip()

    def test_invalid_Language(self):
        with pytest.raises(InvalidLanguageError):
            Language("uui")
