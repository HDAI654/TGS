import strawberry
from src.channel_app.domain.entities.channel import ChannelEntity
from src.channel_app.domain.entities.url_entity import URLEntity


@strawberry.type
class URLType:
    id: str
    url: str

    @staticmethod
    def from_entity(entity: URLEntity) -> "URLType":
        return URLType(
            id=entity.id.value,
            url=entity.url.value,
        )


@strawberry.type
class ChannelType:
    id: str
    name: str
    category: str
    language: str
    country_code: str
    is_geo_blocked: bool
    urls: list[URLType] | None = None

    @staticmethod
    def from_entity(entity: ChannelEntity) -> "ChannelType":
        return ChannelType(
            id=entity.id.value,
            name=entity.name.value,
            category=entity.category.value,
            language=entity.language.value,
            country_code=entity.country_code.value,
            is_geo_blocked=entity.is_geo_blocked.value,
        )
