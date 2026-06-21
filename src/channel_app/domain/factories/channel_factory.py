from src.channel_app.domain.entities.channel import ChannelEntity
from src.core.crypto_utils import IDGenerator
from src.core.id_vo import ID
from src.channel_app.domain.value_objects.name import Name
from src.channel_app.domain.value_objects.url import URL
from src.channel_app.domain.value_objects.language import Language
from src.channel_app.domain.value_objects.is_geo_blocked import IsGeoBlocked


class ChannelFactory:
    @staticmethod
    def create(
        *,
        name: str,
        stream_urls: list[str],
        youtube_urls: list[str],
        languages: list[str],
        country_id: str,
        is_geo_blocked: bool,
        id: str | None = None,
    ) -> ChannelEntity:
        """
        Create a new ChannelEntity.
        """
        if len(stream_urls)+len(youtube_urls) == 0:
            raise ValueError("channel must have at least one stream/youtube url")
        
        if len(languages) == 0:
            raise ValueError("languages can't be empty")

        return ChannelEntity(
            id=ID(IDGenerator.generate()) if id is None else ID(id),
            name=Name(name),
            stream_urls=[URL(u) for u in stream_urls],
            youtube_urls=[URL(u) for u in youtube_urls],
            languages=[Language(l) for l in languages],
            country_id=ID(country_id),
            is_geo_blocked=IsGeoBlocked(is_geo_blocked),
        )
