from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.domain.entities.category import Category
from src.domain.entities.channel import Channel
from src.domain.entities.country import Country
from src.domain.ports.channel_repository import ChannelRepository
from src.domain.ports.country_repository import CountryRepository
from .models import CategoryModel, ChannelModel, CountryModel


def _search_pattern(text: str) -> str:
    """Build a literal case-insensitive SQL LIKE containment pattern."""
    escaped = text.lower().replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


def _urls(value: dict) -> tuple[str, ...]:
    raw_urls = value.get("urls", []) if isinstance(value, dict) else []
    return tuple(raw_urls) if isinstance(raw_urls, list) else ()


def _channel(row: ChannelModel) -> Channel:
    return Channel(
        id=row.id,
        name=row.name,
        category=Category(id=row.category.id, name=row.category.name),
        language=row.language,
        country_code=row.country.country_code,
        urls=_urls(row.urls),
    )


def _country(row: CountryModel) -> Country:
    return Country(
        country_code=row.country_code,
        country_name=row.country_name,
        timezone=row.timezone,
        has_channels=row.has_channels,
        channel_count=row.channel_count,
    )


class SQLAlchemyChannelRepository(ChannelRepository):
    """Read-only SQLAlchemy adapter for channels."""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, channel_id: UUID) -> Channel | None:
        result = await self._session.execute(
            select(ChannelModel)
            .options(
                selectinload(ChannelModel.category),
                selectinload(ChannelModel.country),
            )
            .where(ChannelModel.id == channel_id)
        )
        row = result.scalar_one_or_none()
        return _channel(row) if row else None

    async def get_all(self) -> list[Channel]:
        result = await self._session.execute(
            select(ChannelModel)
            .options(
                selectinload(ChannelModel.category),
                selectinload(ChannelModel.country),
            )
            .order_by(ChannelModel.name, ChannelModel.id)
        )
        return [_channel(row) for row in result.scalars().all()]

    async def search(
        self, text: str, limit: int, offset: int
    ) -> tuple[list[Channel], int]:
        pattern = _search_pattern(text)
        filters = [
            func.lower(ChannelModel.name).like(pattern, escape="\\"),
            func.lower(CategoryModel.name).like(pattern, escape="\\"),
            func.lower(ChannelModel.language).like(pattern, escape="\\"),
            func.lower(ChannelModel.country_code).like(pattern, escape="\\"),
            func.lower(CountryModel.country_name).like(pattern, escape="\\"),
        ]
        base = (
            select(ChannelModel)
            .join(ChannelModel.category)
            .join(ChannelModel.country)
            .where(or_(*filters))
        )
        count_result = await self._session.execute(
            select(func.count(ChannelModel.id))
            .select_from(ChannelModel)
            .join(ChannelModel.category)
            .join(ChannelModel.country)
            .where(or_(*filters))
        )
        total = int(count_result.scalar_one())
        result = await self._session.execute(
            base.options(
                selectinload(ChannelModel.category),
                selectinload(ChannelModel.country),
            )
            .order_by(ChannelModel.name, ChannelModel.id)
            .offset(offset)
            .limit(limit)
        )
        return [_channel(row) for row in result.scalars().all()], total

    async def exist(self, id: UUID) -> bool:
        result = await self._session.execute(
            select(ChannelModel.id).where(ChannelModel.id == id).limit(1)
        )
        return result.scalar_one_or_none() is not None


class SQLAlchemyCountryRepository(CountryRepository):
    """Read-only SQLAlchemy adapter for countries."""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, country_code: str) -> Country | None:
        result = await self._session.execute(
            select(CountryModel).where(CountryModel.country_code == country_code)
        )
        row = result.scalar_one_or_none()
        return _country(row) if row else None

    async def get_all(self) -> list[Country]:
        result = await self._session.execute(
            select(CountryModel).order_by(CountryModel.country_code)
        )
        return [_country(row) for row in result.scalars().all()]

    async def search(
        self, text: str, limit: int, offset: int
    ) -> tuple[list[Country], int]:
        pattern = _search_pattern(text)
        filters = [
            func.lower(CountryModel.country_code).like(pattern, escape="\\"),
            func.lower(CountryModel.country_name).like(pattern, escape="\\"),
            func.lower(CountryModel.timezone).like(pattern, escape="\\"),
        ]
        base = select(CountryModel).where(or_(*filters))
        count_result = await self._session.execute(
            select(func.count(CountryModel.country_code))
            .select_from(CountryModel)
            .where(or_(*filters))
        )
        total = int(count_result.scalar_one())
        result = await self._session.execute(
            base.order_by(CountryModel.country_code)
            .offset(offset)
            .limit(limit)
        )
        return [_country(row) for row in result.scalars().all()], total

    async def exist(self, id: str) -> bool:
        result = await self._session.execute(
            select(CountryModel.country_code)
            .where(CountryModel.country_code == id)
            .limit(1)
        )
        return result.scalar_one_or_none() is not None
