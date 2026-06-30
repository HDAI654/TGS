from shared.domain.entity import Entity
from shared.domain.id_vo import ID
from shared.domain.value_objects.name import Name
from shared.domain.value_objects.category import Category
from shared.domain.value_objects.language import Language
from shared.domain.value_objects.country_code import CountryCode
from shared.domain.value_objects.is_geo_blocked import IsGeoBlocked


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
