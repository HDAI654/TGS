from shared.domain.entities.channel import ChannelEntity
from shared.domain.crypto_utils import IDGenerator
from shared.domain.id_vo import ID
from shared.domain.value_objects.name import Name
from shared.domain.value_objects.category import Category
from shared.domain.value_objects.language import Language
from shared.domain.value_objects.country_code import CountryCode
from shared.domain.value_objects.is_geo_blocked import IsGeoBlocked


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
