from src.core.entity import Entity
from src.core.id_vo import ID
from src.channel_app.domain.value_objects.name import Name
from src.channel_app.domain.value_objects.url import URL
from src.channel_app.domain.value_objects.language import Language
from src.channel_app.domain.value_objects.country_code import CountryCode
from src.channel_app.domain.value_objects.is_geo_blocked import IsGeoBlocked


class ChannelEntity(Entity):
    def __init__(
        self,
        id: ID,
        name: Name,
        category: Name,
        stream_urls: list[URL],
        youtube_urls: list[URL],
        languages: list[Language],
        country_code: CountryCode,
        is_geo_blocked: IsGeoBlocked,
    ):
        self.id = id
        self.name = name
        self.category = category
        self.stream_urls = stream_urls
        self.youtube_urls = youtube_urls
        self.languages = languages
        self.country_code = country_code
        self.is_geo_blocked = is_geo_blocked

        super().__init__()
