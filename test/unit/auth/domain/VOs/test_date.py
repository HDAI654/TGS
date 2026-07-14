import pytest
from src.modules.auth.domain.value_objects.date import Date
from datetime import date
from src.modules.auth.exceptions import InvalidDateError


class TestDate:
    def test_with_datetype(self):
        assert Date(date(1990, 9, 15)).value == date(1990, 9, 15)

    def test_with_strtype(self):
        assert Date("1990-09-15").value == date(1990, 9, 15)

    def test_not_str_date(self):
        with pytest.raises(InvalidDateError):
            Date(25)

    def test_date_strip(self):
        str_date = "        1990-09-15           "
        date_vo = Date(str_date)

        assert date_vo.value == date(1990, 9, 15)

    def test_invalid_date(self):
        with pytest.raises(InvalidDateError):
            Date("A" * 15)
            Date("A" * 25)
