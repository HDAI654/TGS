from src.modules.core.entity import Entity
from src.modules.channels.domain.value_objects.country_code import CountryCode
from src.modules.channels.domain.value_objects.name import Name
from src.modules.channels.domain.value_objects.timezone import Timezone
from src.modules.channels.domain.value_objects.has_channels import HasChannels
from src.modules.channels.domain.value_objects.count import Count


class CountryEntity(Entity):
    FIELD_TYPE_MAP = {
        "country_code": CountryCode,
        "country_name": Name,
        "capital": Name,
        "timezone": Timezone,
        "has_channels": HasChannels,
        "channel_count": Count,
    }

    def __init__(
        self,
        country_code: CountryCode,
        country_name: Name,
        capital: Name,
        timezone: Timezone,
        has_channels: HasChannels,
        channel_count: Count,
    ):
        self.id = id
        self.country_code = country_code
        self.country_name = country_name
        self.capital = capital
        self.timezone = timezone
        self.has_channels = has_channels
        self.channel_count = channel_count

        super().__init__()

    @classmethod
    def create(
        cls,
        country_code: str,
        country_name: str,
        capital: str,
        timezone: str,
        channel_count: int | float,
        has_channels: bool | None = None,
    ) -> "CountryEntity":
        """Create a new CountryEntity."""

        return cls(
            country_code=CountryCode(country_code),
            country_name=Name(country_name),
            capital=Name(capital),
            timezone=Timezone(timezone),
            has_channels=(
                HasChannels(has_channels)
                if has_channels is not None
                else HasChannels(int(channel_count) > 0)
            ),
            channel_count=Count(channel_count),
        )
