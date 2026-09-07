"""Read-only SQLAlchemy adapters for channel and country ports.

Repositories never commit. Search uses case-insensitive literal LIKE with
escaped wildcards. Relationship loading is explicit (selectinload).
"""

from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.exc import DBAPIError, OperationalError, TimeoutError as SATimeoutError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.domain.entities.channel import Channel
from src.domain.entities.country import Country
from src.domain.ports.channel_repository import ChannelRepository
from src.domain.ports.country_repository import CountryRepository
from src.exceptions.infrastructure import (
    DatabaseConnectionError,
    DatabaseOperationError,
    DatabaseTimeoutError,
)
from src.infrastructure.persistence.mappers import to_channel, to_country
from src.infrastructure.persistence.search import search_pattern
from src.infrastructure.persistence.models import (
    CategoryModel,
    ChannelModel,
    CountryModel,
)


def _translate_db_error(exc: Exception) -> Exception:
    """Map SQLAlchemy/driver failures to project infrastructure errors."""
    if isinstance(exc, SATimeoutError):
        return DatabaseTimeoutError("Database operation timed out")
    if isinstance(exc, OperationalError):
        return DatabaseConnectionError("Database connection failed")
    if isinstance(exc, DBAPIError):
        return DatabaseOperationError("Database operation failed")
    return DatabaseOperationError("Database operation failed")


class SQLAlchemyChannelRepository(ChannelRepository):
    """Read-only SQLAlchemy adapter for channels."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, channel_id: UUID) -> Channel | None:
        try:
            result = await self._session.execute(
                select(ChannelModel)
                .options(
                    selectinload(ChannelModel.category),
                    selectinload(ChannelModel.country),
                )
                .where(ChannelModel.id == channel_id)
            )
            row = result.scalar_one_or_none()
            return to_channel(row) if row else None
        except (OperationalError, SATimeoutError, DBAPIError) as exc:
            raise _translate_db_error(exc) from exc

    async def get_all(self) -> list[Channel]:
        try:
            result = await self._session.execute(
                select(ChannelModel)
                .options(
                    selectinload(ChannelModel.category),
                    selectinload(ChannelModel.country),
                )
                .order_by(ChannelModel.name, ChannelModel.id)
            )
            return [to_channel(row) for row in result.scalars().all()]
        except (OperationalError, SATimeoutError, DBAPIError) as exc:
            raise _translate_db_error(exc) from exc

    async def search(
        self, text: str, limit: int, offset: int
    ) -> tuple[list[Channel], int]:
        pattern = search_pattern(text)
        filters = [
            func.lower(ChannelModel.name).like(pattern, escape="\\"),
            func.lower(CategoryModel.name).like(pattern, escape="\\"),
            func.lower(ChannelModel.language).like(pattern, escape="\\"),
            func.lower(ChannelModel.country_code).like(pattern, escape="\\"),
            func.lower(CountryModel.country_name).like(pattern, escape="\\"),
        ]
        try:
            count_result = await self._session.execute(
                select(func.count(ChannelModel.id))
                .select_from(ChannelModel)
                .join(ChannelModel.category)
                .join(ChannelModel.country)
                .where(or_(*filters))
            )
            total = int(count_result.scalar_one())
            result = await self._session.execute(
                select(ChannelModel)
                .join(ChannelModel.category)
                .join(ChannelModel.country)
                .where(or_(*filters))
                .options(
                    selectinload(ChannelModel.category),
                    selectinload(ChannelModel.country),
                )
                .order_by(ChannelModel.name, ChannelModel.id)
                .offset(offset)
                .limit(limit)
            )
            return [to_channel(row) for row in result.scalars().all()], total
        except (OperationalError, SATimeoutError, DBAPIError) as exc:
            raise _translate_db_error(exc) from exc

    async def exist(self, id: UUID) -> bool:
        try:
            result = await self._session.execute(
                select(ChannelModel.id).where(ChannelModel.id == id).limit(1)
            )
            return result.scalar_one_or_none() is not None
        except (OperationalError, SATimeoutError, DBAPIError) as exc:
            raise _translate_db_error(exc) from exc


class SQLAlchemyCountryRepository(CountryRepository):
    """Read-only SQLAlchemy adapter for countries."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, country_code: str) -> Country | None:
        try:
            result = await self._session.execute(
                select(CountryModel).where(CountryModel.country_code == country_code)
            )
            row = result.scalar_one_or_none()
            return to_country(row) if row else None
        except (OperationalError, SATimeoutError, DBAPIError) as exc:
            raise _translate_db_error(exc) from exc

    async def get_all(self) -> list[Country]:
        try:
            result = await self._session.execute(
                select(CountryModel).order_by(CountryModel.country_code)
            )
            return [to_country(row) for row in result.scalars().all()]
        except (OperationalError, SATimeoutError, DBAPIError) as exc:
            raise _translate_db_error(exc) from exc

    async def search(
        self, text: str, limit: int, offset: int
    ) -> tuple[list[Country], int]:
        pattern = search_pattern(text)
        filters = [
            func.lower(CountryModel.country_code).like(pattern, escape="\\"),
            func.lower(CountryModel.country_name).like(pattern, escape="\\"),
            func.lower(CountryModel.timezone).like(pattern, escape="\\"),
        ]
        try:
            count_result = await self._session.execute(
                select(func.count(CountryModel.country_code))
                .select_from(CountryModel)
                .where(or_(*filters))
            )
            total = int(count_result.scalar_one())
            result = await self._session.execute(
                select(CountryModel)
                .where(or_(*filters))
                .order_by(CountryModel.country_code)
                .offset(offset)
                .limit(limit)
            )
            return [to_country(row) for row in result.scalars().all()], total
        except (OperationalError, SATimeoutError, DBAPIError) as exc:
            raise _translate_db_error(exc) from exc

    async def exist(self, id: str) -> bool:
        try:
            result = await self._session.execute(
                select(CountryModel.country_code)
                .where(CountryModel.country_code == id)
                .limit(1)
            )
            return result.scalar_one_or_none() is not None
        except (OperationalError, SATimeoutError, DBAPIError) as exc:
            raise _translate_db_error(exc) from exc
