import pytest
from src.modules.channels.domain.value_objects.country_code import CountryCode
from src.modules.channels.exceptions import InvalidCountryCodeError


class TestCountryCode:
    def test_not_str_country_code(self):
        with pytest.raises(InvalidCountryCodeError):
            CountryCode(25)
            CountryCode(None)

    def test_empty_str_country_code(self):
        with pytest.raises(InvalidCountryCodeError):
            CountryCode("")
            CountryCode(" ")
            CountryCode("  ")

    def test_country_code_strip(self):
        str_country_code = "        UK  "
        country_code = CountryCode(str_country_code)

        assert country_code.value == str_country_code.strip()

    def test_country_code_upper(self):
        str_country_code = "us"
        country_code = CountryCode(str_country_code)

        assert country_code.value == str_country_code.upper()

    def test_invalid_country_code(self):
        with pytest.raises(InvalidCountryCodeError):
            CountryCode("invalid country code")
