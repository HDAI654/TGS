import pytest
from src.modules.channels.domain.value_objects.timezone import Timezone
from src.modules.channels.exceptions import InvalidTimezoneError


class TestTimezone:
    def test_not_str_timezone(self):
        with pytest.raises(InvalidTimezoneError):
            Timezone(25)
            Timezone(None)

    def test_empty_str_timezone(self):
        with pytest.raises(InvalidTimezoneError):
            Timezone("")
            Timezone(" ")
            Timezone("  ")

    def test_timezone_strip(self):
        str_timezone = "        Europe/London  "
        timezone = Timezone(str_timezone)

        assert timezone.value == str_timezone.strip()

    def test_invalid_timezone(self):
        with pytest.raises(InvalidTimezoneError):
            Timezone("Mytimezone")
