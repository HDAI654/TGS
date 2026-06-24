from src.core.entity import Entity
from src.core.id_vo import ID
from src.channel_app.domain.value_objects.name import Name
from src.channel_app.domain.value_objects.category import Category
from src.channel_app.domain.value_objects.language import Language
from src.channel_app.domain.value_objects.country_code import CountryCode
from src.channel_app.domain.value_objects.is_geo_blocked import IsGeoBlocked


class ChannelEntity(Entity):
    FIELD_TYPE_MAP = {
        "id": ID,
        "name": Name,
        "category": Category,
        "language": Language,
        "country_code": CountryCode,
        "is_geo_blocked": IsGeoBlocked,
    }

    def __init__(
        self,
        id: ID,
        name: Name,
        category: Category,
        language: Language,
        country_code: CountryCode,
        is_geo_blocked: IsGeoBlocked,
    ):
        self.id = id
        self.name = name
        self.category = category
        self.language = language
        self.country_code = country_code
        self.is_geo_blocked = is_geo_blocked

        super().__init__()
