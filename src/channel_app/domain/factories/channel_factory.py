from src.channel_app.domain.entities.channel import ChannelEntity
from src.core.crypto_utils import IDGenerator
from src.core.id_vo import ID
from src.channel_app.domain.value_objects.name import Name
from src.channel_app.domain.value_objects.category import Category
from src.channel_app.domain.value_objects.language import Language
from src.channel_app.domain.value_objects.country_code import CountryCode
from src.channel_app.domain.value_objects.is_geo_blocked import IsGeoBlocked


class ChannelFactory:
    @staticmethod
    def create(
        *,
        name: str,
        category: str,
        language: str,
        country_code: str,
        is_geo_blocked: bool,
        id: str | None = None,
    ) -> ChannelEntity:
        """
        Create a new ChannelEntity.
        """
        return ChannelEntity(
            id=ID(IDGenerator.generate()) if id is None else ID(id),
            name=Name(name),
            category=Category(category),
            language=Language(language),
            country_code=CountryCode(country_code),
            is_geo_blocked=IsGeoBlocked(is_geo_blocked),
        )
