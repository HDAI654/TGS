"""Strawberry GraphQL schema for the public read-only channels API.

Presentation maps protocol input to application queries and domain entities
to GraphQL types. Business rules stay out of this layer.
"""

from uuid import UUID

import strawberry
from strawberry.types import Info

from src.application.queries.channel_queries import (
    get_channel,
    search_channels,
)
from src.application.queries.country_queries import (
    get_country,
    get_all_countries,
    search_countries,
)
from src.application.queries.count_query import get_count
from src.domain.entities.channel import Channel
from src.domain.entities.country import Country


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


@strawberry.type
class Countries:
    items: list[CountryType]


@strawberry.type
class Count:
    channels: int
    countries: int


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
        self,
        limit: int,
        offset: int,
        info: Info,
        search: str | None = None,
    ) -> ChannelConnection | None:
        result = await search_channels(
            info.context["channel_repository"], search, limit, offset
        )
        if result is None:
            return None
        items, total = result
        return ChannelConnection(
            items=[channel_type(item) for item in items],
            total=total,
            limit=limit,
            offset=offset,
        )

    @strawberry.field
    async def country(self, country_code: str, info: Info) -> CountryType | None:
        entity = await get_country(info.context["country_repository"], country_code)
        return country_type(entity) if entity else None

    @strawberry.field
    async def countries(
        self,
        limit: int,
        offset: int,
        info: Info,
        search: str | None = None,
    ) -> CountryConnection | None:
        result = await search_countries(
            info.context["country_repository"], search, limit, offset
        )
        if result is None:
            return None
        items, total = result
        return CountryConnection(
            items=[country_type(item) for item in items],
            total=total,
            limit=limit,
            offset=offset,
        )

    @strawberry.field
    async def all_countries(
        self,
        info: Info,
    ) -> CountryConnection | None:
        result = await get_all_countries(info.context["country_repository"])
        return Countries(
            items=[country_type(item) for item in result],
        )

    @strawberry.field
    async def count(
        self,
    ) -> Count | None:
        result = await get_count()
        return Count(
            channels=result["channels"],
            countries=result["countries"],
        )


schema = strawberry.Schema(query=Query)
