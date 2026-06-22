from src.core.entity import Entity
from src.core.id_vo import ID
from src.channel_app.domain.value_objects.country_code import CountryCode
from src.channel_app.domain.value_objects.name import Name
from src.channel_app.domain.value_objects.timezone import Timezone
from src.channel_app.domain.value_objects.has_channels import HasChannels
from src.channel_app.domain.value_objects.count import Count


class CountryEntity(Entity):
    def __init__(
        self,
        id: ID,
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
