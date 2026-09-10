"""SQLAlchemy implementation for channel repository interface."""

import logging
from uuid import UUID
from sqlalchemy import func, or_, select, exists
from sqlalchemy.exc import (
    IntegrityError,
    OperationalError,
    SQLAlchemyError,
    TimeoutError,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from src.domain.entities.channel import Channel
from src.domain.ports import ChannelRepository
from src.exceptions.infrastructure import (
    DatabaseConnectionError,
    DatabaseOperationError,
    DatabaseTimeoutError,
)
from src.infrastructure.persistence.mappers import to_channel
from src.infrastructure.persistence.search import search_pattern
from src.infrastructure.persistence.models import (
    CategoryModel,
    ChannelModel,
    CountryModel,
)

logger = logging.getLogger(__name__)


class SQLAlchemyChannelRepository(ChannelRepository):
    """Read-only SQLAlchemy adapter for channels."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, channel_id: UUID) -> Channel | None:
        logger.debug("Fetching channel by id: id=%s", channel_id)
        result = await self._execute_db_operation(
            "get_channel_by_id",
            self._session.execute,
            select(ChannelModel)
            .options(
                selectinload(ChannelModel.category),
                selectinload(ChannelModel.country),
            )
            .where(ChannelModel.id == channel_id),
        )

        row = result.scalar_one_or_none()
        channel = to_channel(row) if row else None

        if channel:
            logger.debug("Channel found: id=%s name=%s", channel_id, channel.name)
        else:
            logger.debug("Channel not found: id=%s", channel_id)

        return channel

    async def get_all(self) -> list[Channel]:
        logger.debug("Fetching all channels")
        result = await self._execute_db_operation(
            "get_all_channels",
            self._session.execute,
            select(ChannelModel)
            .options(
                selectinload(ChannelModel.category),
                selectinload(ChannelModel.country),
            )
            .order_by(ChannelModel.name, ChannelModel.id),
        )

        channels = [to_channel(row) for row in result.scalars().all()]

        logger.debug("Retrieved %d channels", len(channels))
        return channels

    async def search(
        self, text: str, limit: int, offset: int
    ) -> tuple[list[Channel], int]:
        logger.debug(
            "Searching channels: text='%s', limit=%d, offset=%d", text, limit, offset
        )
        pattern = search_pattern(text)
        filters = [
            func.lower(ChannelModel.name).like(pattern, escape="\\"),
            func.lower(CategoryModel.name).like(pattern, escape="\\"),
            func.lower(ChannelModel.language).like(pattern, escape="\\"),
            func.lower(ChannelModel.country_code).like(pattern, escape="\\"),
            func.lower(CountryModel.country_name).like(pattern, escape="\\"),
        ]
        count_result = await self._execute_db_operation(
            "count_search_channel",
            self._session.execute,
            select(func.count(ChannelModel.id))
            .select_from(ChannelModel)
            .join(ChannelModel.category)
            .join(ChannelModel.country)
            .where(or_(*filters)),
        )

        total = int(count_result.scalar_one())
        result = await self._execute_db_operation(
            "search_channel",
            self._session.execute,
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
            .limit(limit),
        )
        channels = [to_channel(row) for row in result.scalars().all()]

        logger.debug(
            "Search returned %d channels (page %d-%d of %d)",
            len(channels),
            offset + 1,
            min(offset + limit, total),
            total,
        )
        return channels, total

    async def exist(self, id: UUID) -> bool:
        logger.debug("Checking if channel exists: id=%s", id)
        result = await self._execute_db_operation(
            "exist_channel",
            self._session.execute,
            select(exists().where(ChannelModel.id == id)),
        )
        res = result.scalar()
        logger.debug("Channel exists check completed: id=%s exists=%s", id, res)
        return res

    async def count_channels(self) -> int:
        """Return the total number of channels."""
        logger.debug("Counting all channels")

        result = await self._execute_db_operation(
            "count_channels",
            self._session.execute,
            select(func.count(ChannelModel.id)),
        )

        total = int(result.scalar_one())
        logger.debug("Total channels: %d", total)

        return total

    async def _execute_db_operation(self, operation: str, coro, *args, **kwargs):
        try:
            return await coro(*args, **kwargs)
        except IntegrityError as e:
            logger.exception("Database integrity error during %s", operation)
            raise DatabaseOperationError(f"Database integrity error: {e}") from e
        except OperationalError as e:
            logger.exception("Database connection error during %s", operation)
            raise DatabaseConnectionError(f"Failed to connect to database: {e}") from e
        except TimeoutError as e:
            logger.exception("Database timeout during %s", operation)
            raise DatabaseTimeoutError(f"Database operation timed out: {e}") from e
        except SQLAlchemyError as e:
            logger.exception("Database error during %s", operation)
            raise DatabaseOperationError(f"Database operation failed: {e}") from e
