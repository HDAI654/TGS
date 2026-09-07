"""Explicit mappers between ORM models and domain entities.

Domain entities never depend on SQLAlchemy types.
"""

from src.domain.entities.category import Category
from src.domain.entities.channel import Channel
from src.domain.entities.country import Country
from src.infrastructure.persistence.models import (
    ChannelModel,
    CountryModel,
)


def _urls(value: object) -> tuple[str, ...]:
    if not isinstance(value, dict):
        return ()
    raw = value.get("urls", [])
    return tuple(raw) if isinstance(raw, list) else ()


def to_category(row_id: int, name: str) -> Category:
    return Category(id=row_id, name=name)


def to_channel(row: ChannelModel) -> Channel:
    return Channel(
        id=row.id,
        name=row.name,
        category=to_category(row.category.id, row.category.name),
        language=row.language,
        country_code=row.country.country_code,
        urls=_urls(row.urls),
    )


def to_country(row: CountryModel) -> Country:
    return Country(
        country_code=row.country_code,
        country_name=row.country_name,
        timezone=row.timezone,
        has_channels=row.has_channels,
        channel_count=row.channel_count,
    )
