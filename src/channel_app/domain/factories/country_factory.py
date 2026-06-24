from src.channel_app.domain.entities.country import CountryEntity
from src.channel_app.domain.value_objects.country_code import CountryCode
from src.channel_app.domain.value_objects.name import Name
from src.channel_app.domain.value_objects.timezone import Timezone
from src.channel_app.domain.value_objects.has_channels import HasChannels
from src.channel_app.domain.value_objects.count import Count


class CountryFactory:
    @staticmethod
    def create(
        *,
        country_code: str,
        country_name: str,
        capital: str,
        timezone: str,
        channel_count: int | float,
    ) -> CountryEntity:
        """
        Create a new CountryEntity.
        """
        return CountryEntity(
            country_code=CountryCode(country_code),
            country_name=Name(country_name),
            capital=Name(capital),
            timezone=Timezone(timezone),
            has_channels=HasChannels(int(channel_count) > 0),
            channel_count=Count(channel_count),
        )
