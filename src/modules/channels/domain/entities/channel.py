from src.modules.core.entity import Entity
from src.modules.channels.domain.value_objects.id import ID
from src.modules.channels.domain.value_objects.name import Name
from src.modules.channels.domain.value_objects.category import Category
from src.modules.channels.domain.value_objects.language import Language
from src.modules.channels.domain.value_objects.country_code import CountryCode
from src.modules.channels.domain.value_objects.is_geo_blocked import IsGeoBlocked


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

    @classmethod
    def create(
        cls,
        name: str,
        category: str,
        language: str,
        country_code: str,
        is_geo_blocked: bool,
        id: str | None = None,
    ) -> "ChannelEntity":
        """Create a new ChannelEntity."""

        return cls(
            id=ID(id) if id is not None else ID.generate(),
            name=Name(name),
            category=Category(category),
            language=Language(language),
            country_code=CountryCode(country_code),
            is_geo_blocked=IsGeoBlocked(is_geo_blocked),
        )
