import logging
from typing import Tuple

from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError, OperationalError, TimeoutError as SATimeoutError

from src.modules.channels.domain.entities.channel import Channel
from src.modules.channels.domain.ports.channel_repo_interface import ChannelRepository
from src.modules.channels.infrastructure.persistence.models import ChannelModel
from src.modules.channels.domain.exceptions import ChannelNotFoundError
from src.modules.channels.infrastructure.exceptions import (
    DatabaseConnectionError,
    DatabaseTimeoutError,
    DatabaseOperationError,
)

logger = logging.getLogger(__name__)


class PostgresChannelRepository(ChannelRepository):
    """PostgreSQL implementation of ChannelRepository using async SQLAlchemy."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, channel_id: str) -> Channel:
        try:
            stmt = select(ChannelModel).where(ChannelModel.id == channel_id)
            result = await self._session.execute(stmt)
            model = result.scalar_one()
        except OperationalError as exc:
            logger.error("Database connection failed for channel_id: %s", channel_id, exc_info=True)
            raise DatabaseConnectionError("Database connection failed") from exc
        except SATimeoutError as exc:
            logger.error("Database timeout for channel_id: %s", channel_id, exc_info=True)
            raise DatabaseTimeoutError("Database operation timed out") from exc
        except SQLAlchemyError as exc:
            logger.error("Database operation failed for channel_id: %s", channel_id, exc_info=True)
            raise DatabaseOperationError("Database operation failed") from exc
        except Exception as exc:
            logger.error("Unexpected database error for channel_id: %s", channel_id, exc_info=True)
            raise DatabaseOperationError("Unexpected database error") from exc

        if model is None:
            raise ChannelNotFoundError(f"Channel with id {channel_id} not found")

        return self._to_domain(model)

    async def search(self, text: str, limit: int, offset: int) -> Tuple[Channel, ...]:
        logger.debug("Searching channels with text='%s', limit=%d, offset=%d", text, limit, offset)
        try:
            search_pattern = f"%{text.lower()}%"
            stmt = (
                select(ChannelModel)
                .where(
                    or_(
                        func.lower(ChannelModel.name).like(search_pattern),
                        func.lower(ChannelModel.category).like(search_pattern),
                        func.lower(ChannelModel.language).like(search_pattern),
                        func.lower(ChannelModel.country_code).like(search_pattern),
                    )
                )
                .offset(offset)
                .limit(limit)
            )
            result = await self._session.execute(stmt)
            models = result.scalars().all()
        except OperationalError as exc:
            logger.error("Database connection failed during search", exc_info=True)
            raise DatabaseConnectionError("Database connection failed") from exc
        except SATimeoutError as exc:
            logger.error("Database timeout during search", exc_info=True)
            raise DatabaseTimeoutError("Database operation timed out") from exc
        except SQLAlchemyError as exc:
            logger.error("Database operation failed during search", exc_info=True)
            raise DatabaseOperationError("Database operation failed") from exc
        except Exception as exc:
            logger.error("Unexpected database error during search", exc_info=True)
            raise DatabaseOperationError("Unexpected database error") from exc

        return tuple(self._to_domain(m) for m in models)

    async def exists_by_id(self, channel_id: str) -> bool:
        try:
            stmt = select(ChannelModel.id).where(ChannelModel.id == channel_id)
            result = await self._session.execute(stmt)
            return result.scalar() is not None
        except OperationalError as exc:
            logger.error("Database connection failed for exists check, channel_id: %s", channel_id, exc_info=True)
            raise DatabaseConnectionError("Database connection failed") from exc
        except SATimeoutError as exc:
            logger.error("Database timeout for exists check, channel_id: %s", channel_id, exc_info=True)
            raise DatabaseTimeoutError("Database operation timed out") from exc
        except SQLAlchemyError as exc:
            logger.error("Database operation failed for exists check, channel_id: %s", channel_id, exc_info=True)
            raise DatabaseOperationError("Database operation failed") from exc
        except Exception as exc:
            logger.error("Unexpected database error for exists check, channel_id: %s", channel_id, exc_info=True)
            raise DatabaseOperationError("Unexpected database error") from exc

    @staticmethod
    def _to_domain(model: ChannelModel) -> Channel:
        return Channel(
            id=model.id,
            name=model.name,
            category=model.category,
            language=model.language,
            country_code=model.country_code,
            urls=tuple(model.urls) if model.urls else (),
        )