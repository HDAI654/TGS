import pytest
from src.modules.channels.domain.value_objects.name import Name
from src.modules.channels.exceptions import InvalidNameError


class TestName:
    def test_not_str_name(self):
        with pytest.raises(InvalidNameError):
            Name(25)
            Name(None)

    def test_empty_str_name(self):
        with pytest.raises(InvalidNameError):
            Name("")
            Name(" ")
            Name("  ")

    def test_name_strip(self):
        str_name = "        name  "
        name = Name(str_name)

        assert name.value == str_name.strip()

    def test_long_name(self):
        with pytest.raises(InvalidNameError):
            Name("Myname" + "ABC" * 100)
