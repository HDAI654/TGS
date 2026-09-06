from uuid import UUID

import strawberry
from strawberry.types import Info
from channels_service.application.errors import InvalidPaginationError
from channels_service.application.queries.channel_queries import (
    get_channel,
    search_channels,
)
from channels_service.application.queries.country_queries import (
    get_country,
    search_countries,
)
from channels_service.domain.entities.category import Category
from channels_service.domain.entities.channel import Channel
from channels_service.domain.entities.country import Country


@strawberry.type
class CategoryType:
    id: int
    name: str


@strawberry.type
class ChannelType:
    id: UUID
    name: str
    category: CategoryType
    language: str
    country_code: str
    urls: list[str]


@strawberry.type
class CountryType:
    country_code: str
    country_name: str
    timezone: str
    has_channels: bool
    channel_count: int


@strawberry.type
class ChannelConnection:
    items: list[ChannelType]
    total: int
    limit: int
    offset: int


@strawberry.type
class CountryConnection:
    items: list[CountryType]
    total: int
    limit: int
    offset: int


def channel_type(entity: Channel) -> ChannelType:
    return ChannelType(
        id=entity.id,
        name=entity.name,
        category=CategoryType(id=entity.category.id, name=entity.category.name),
        language=entity.language,
        country_code=entity.country_code,
        urls=list(entity.urls),
    )


def country_type(entity: Country) -> CountryType:
    return CountryType(
        country_code=entity.country_code,
        country_name=entity.country_name,
        timezone=entity.timezone,
        has_channels=entity.has_channels,
        channel_count=entity.channel_count,
    )


@strawberry.type
class Query:
    @strawberry.field
    async def channel(self, id: UUID, info: Info) -> ChannelType | None:
        entity = await get_channel(info.context["channel_repository"], id)
        return channel_type(entity) if entity else None

    @strawberry.field
    async def channels(
        self, limit: int, offset: int, info: Info, search: str | None = None
    ) -> ChannelConnection | None:
        if not 1 <= limit <= 100:
            raise InvalidPaginationError("limit must be between 1 and 100")
        if offset < 0:
            raise InvalidPaginationError("offset must be non-negative")
        result = await search_channels(
            info.context["channel_repository"], search, limit, offset
        )
        if result is None:
            return None
        items, total = result
        return ChannelConnection(
            [channel_type(item) for item in items], total, limit, offset
        )

    @strawberry.field
    async def country(self, country_code: str, info: Info) -> CountryType | None:
        entity = await get_country(info.context["country_repository"], country_code)
        return country_type(entity) if entity else None

    @strawberry.field
    async def countries(
        self, limit: int, offset: int, info: Info, search: str | None = None
    ) -> CountryConnection | None:
        if not 1 <= limit <= 100:
            raise InvalidPaginationError("limit must be between 1 and 100")
        if offset < 0:
            raise InvalidPaginationError("offset must be non-negative")
        result = await search_countries(
            info.context["country_repository"], search, limit, offset
        )
        if result is None:
            return None
        items, total = result
        return CountryConnection(
            [country_type(item) for item in items], total, limit, offset
        )


schema = strawberry.Schema(query=Query)
