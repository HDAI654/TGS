from shared.domain.entity import Entity
from shared.domain.value_objects.country_code import CountryCode
from shared.domain.value_objects.name import Name
from shared.domain.value_objects.timezone import Timezone
from shared.domain.value_objects.has_channels import HasChannels
from shared.domain.value_objects.count import Count


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
