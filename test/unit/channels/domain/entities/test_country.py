from src.modules.channels.domain.entities.country import CountryEntity
from src.modules.channels.domain.value_objects.country_code import CountryCode
from src.modules.channels.domain.value_objects.name import Name
from src.modules.channels.domain.value_objects.timezone import Timezone
from src.modules.channels.domain.value_objects.has_channels import HasChannels
from src.modules.channels.domain.value_objects.count import Count


class TestCountryEntity:
    def test_create_success(self):
        country_code = "US"
        country_name = "United States"
        capital = "Washington"
        timezone = "America/New_York"
        has_channels = True
        channel_count = 30

        country = CountryEntity.create(
            country_code=country_code,
            country_name=country_name,
            capital=capital,
            timezone=timezone,
            has_channels=has_channels,
            channel_count=channel_count,
        )

        assert isinstance(country.country_code, CountryCode)
        assert country.country_code.value == country_code

        assert isinstance(country.country_name, Name)
        assert country.country_name.value == country_name

        assert isinstance(country.capital, Name)
        assert country.capital.value == capital

        assert isinstance(country.timezone, Timezone)
        assert country.timezone.value == timezone

        assert isinstance(country.has_channels, HasChannels)
        assert country.has_channels.value == has_channels

        assert isinstance(country.channel_count, Count)
        assert country.channel_count.value == channel_count

    def test_create_with_vos(self):
        country_code = CountryCode("US")
        country_name = Name("United States")
        capital = Name("Washington")
        timezone = Timezone("America/New_York")
        has_channels = HasChannels(True)
        channel_count = Count(30)

        country = CountryEntity(
            country_code=country_code,
            country_name=country_name,
            capital=capital,
            timezone=timezone,
            has_channels=has_channels,
            channel_count=channel_count,
        )

        assert isinstance(country.country_code, CountryCode)
        assert country.country_code.value == country_code.value

        assert isinstance(country.country_name, Name)
        assert country.country_name.value == country_name.value

        assert isinstance(country.capital, Name)
        assert country.capital.value == capital.value

        assert isinstance(country.timezone, Timezone)
        assert country.timezone.value == timezone.value

        assert isinstance(country.has_channels, HasChannels)
        assert country.has_channels.value == has_channels.value

        assert isinstance(country.channel_count, Count)
        assert country.channel_count.value == channel_count.value
