import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import insert
from src.modules.channels.infrastructure.persistence.models import ChannelModel, CountryModel, URLModel
from workers.ports.repo_interface import IRepo
from src.modules.channels.domain.value_objects.id import ID
from src.modules.channels.domain.entities.channel import ChannelEntity
from src.modules.channels.domain.entities.country import CountryEntity
from src.modules.channels.domain.entities.url_entity import URLEntity
from sqlalchemy.exc import (
    IntegrityError,
    OperationalError,
    TimeoutError,
    SQLAlchemyError,
)
from workers.core.exceptions import (
    DatabaseOperationError,
    DatabaseConnectionError,
    DatabaseTimeoutError,
)

logger = logging.getLogger(__name__)


class SQLAL_Repo(IRepo):
    """SQLAlchemy implemantation for channel, country and URL entities."""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def upsert_batch_channels(self, channels: list[ChannelEntity]) -> None:
        if not channels:
            return

        logger.info("Upserting %s channels", len(channels))

        # Convert entities to dict
        values = [
            {
                "nano_id": c.id.value,
                "name": c.name.value,
                "category": c.category.value,
                "language": c.language.value,
                "country_code": c.country_code.value,
                "is_geo_blocked": c.is_geo_blocked.value,
            }
            for c in channels
        ]

        # Build upsert statement
        stmt = insert(ChannelModel).values(values)
        stmt = stmt.on_conflict_do_update(
            index_elements=["nano_id"],
            set_={
                "name": stmt.excluded.name,
                "category": stmt.excluded.category,
                "language": stmt.excluded.language,
                "country_code": stmt.excluded.country_code,
                "is_geo_blocked": stmt.excluded.is_geo_blocked,
                "updated_at": func.now(),
            },
        )

        # Execute (single query)
        await self._execute_db_operation(
            "upsert_channels",
            self._session.execute,
            stmt,
        )

        logger.info("Successfully upserted %s channels", len(channels))

    async def upsert_batch_countries(self, countries: list[CountryEntity]) -> None:
        if not countries:
            return

        logger.info("Upserting %s countries", len(countries))

        # Convert entities to dict
        values = [
            {
                "country_code": c.country_code.value,
                "country_name": c.country_name.value,
                "capital": c.capital.value,
                "timezone": c.timezone.value,
                "has_channels": c.has_channels.value,
                "channel_count": c.channel_count.value,
            }
            for c in countries
        ]

        # Build upsert statement
        stmt = insert(CountryModel).values(values)
        stmt = stmt.on_conflict_do_update(
            index_elements=["country_code"],
            set_={
                "country_name": stmt.excluded.country_name,
                "capital": stmt.excluded.capital,
                "timezone": stmt.excluded.timezone,
                "has_channels": stmt.excluded.has_channels,
                "channel_count": stmt.excluded.channel_count,
                "updated_at": func.now(),
            },
        )

        # Execute (single query)
        await self._execute_db_operation(
            "upsert_countries",
            self._session.execute,
            stmt,
        )

        logger.info("Successfully upserted %s countries", len(countries))

    async def upsert_batch_urls(self, urls: list[tuple[ID, URLEntity]]) -> None:
        if not urls:
            return

        logger.info("Upserting %s URLs", len(urls))

        # Convert entities to dict
        values = [
            {
                "nano_id": url_entity.id.value,
                "channel_id": channel_id.value,
                "url": url_entity.url.value,
            }
            for channel_id, url_entity in urls
        ]

        # Build upsert statement
        stmt = insert(URLModel).values(values)
        stmt = stmt.on_conflict_do_update(
            index_elements=["channel_id", "url"],
            set_={
                "channel_id": stmt.excluded.channel_id,
                "url": stmt.excluded.url,
                "updated_at": func.now(),
            },
        )

        # Execute (single query)
        await self._execute_db_operation(
            "upsert_urls",
            self._session.execute,
            stmt,
        )

        logger.info("Successfully upserted %s URLs", len(urls))

    async def _execute_db_operation(self, operation: str, coro, *args, **kwargs):
        try:
            return await coro(*args, **kwargs)
        except IntegrityError as e:
            logger.exception(f"Database integrity error during {operation}")
            raise DatabaseOperationError(f"Database integrity error: {e}") from e
        except OperationalError as e:
            logger.exception(f"Database connection error during {operation}")
            raise DatabaseConnectionError(f"Failed to connect to database: {e}") from e
        except TimeoutError as e:
            logger.exception(f"Database timeout during {operation}")
            raise DatabaseTimeoutError(f"Database operation timed out: {e}") from e
        except SQLAlchemyError as e:
            logger.exception(f"Database error during {operation}")
            raise DatabaseOperationError(f"Database operation failed: {e}") from e
