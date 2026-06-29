import pytest
from shared.domain.factories.country_factory import CountryFactory


class TestChannelFactory:
    def test_create_success(self):
        country = CountryFactory.create(
            country_code="US",
            country_name="United States of America",
            capital="Washington, D.C.",
            timezone="America/New_York",
            channel_count=8,
        )

        assert country.country_code.value == "US"
        assert country.country_name.value == "United States of America"
        assert country.capital.value == "Washington, D.C."
        assert country.timezone.value == "America/New_York"
        assert country.channel_count.value == 8
        assert country.has_channels.value == True

    def test_create_with_zero_channel_count(self):
        country = CountryFactory.create(
            country_code="US",
            country_name="United States of America",
            capital="Washington, D.C.",
            timezone="America/New_York",
            channel_count=0,
        )
        assert country.has_channels.value is False
