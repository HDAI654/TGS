from src.modules.core.entity import Entity
from src.modules.channels.domain.value_objects.id import ID
from src.modules.channels.domain.value_objects.name import Name
from src.modules.channels.domain.value_objects.language import Language
from src.modules.channels.domain.value_objects.country_code import CountryCode


class ChannelEntity(Entity):
    def __init__(
        self,
        id: ID,
        name: Name,
        category_id: ID,
        language: Language,
        country_code: CountryCode,
    ):
        self.id = id
        self.name = name
        self.category_id = category_id
        self.language = language
        self.country_code = country_code

        super().__init__()

    @classmethod
    def create(
        cls,
        name: str,
        category_id: str,
        language: str,
        country_code: str,
        id: str | None = None,
    ) -> "ChannelEntity":
        """Create a new ChannelEntity."""

        return cls(
            id=ID(id) if id is not None else ID.generate(),
            name=Name(name),
            category=ID(category_id),
            language=Language(language),
            country_code=CountryCode(country_code),
        )
