from sqlalchemy.ext.asyncio import AsyncSession
import logging
from src.channel_app.domain.ports.unit_of_work_interface import (
    IUnitOfWork,
)
from src.channel_app.infrastructure.persistence.sqlal_country_repo import (
    SQLAL_CountryRepository,
)
from src.channel_app.infrastructure.persistence.sqlal_channel_repo import (
    SQLAL_ChannelRepository,
)
from sqlalchemy.exc import (
    OperationalError,
    TimeoutError,
    SQLAlchemyError,
)
from src.core.exceptions import (
    DatabaseOperationError,
    DatabaseConnectionError,
    DatabaseTimeoutError,
)

logger = logging.getLogger(__name__)


class SQLAL_UnitOfWork(IUnitOfWork):

    def __init__(self, session: AsyncSession):
        self._session = session

        self.countries = SQLAL_CountryRepository(session)
        self.channels = SQLAL_ChannelRepository(session)

    async def commit(self) -> None:
        logger.debug("Committing transaction")

        try:
            await self._execute_db_operation(
                "commit",
                self._session.commit,
            )

            logger.debug("Transaction committed successfully")

        except Exception:
            logger.warning("Transaction commit failed, rolling back")

            await self._session.rollback()

            logger.debug("Transaction rollback completed after commit failure")

            raise

    async def rollback(self) -> None:
        logger.debug("Rolling back transaction")

        await self._execute_db_operation(
            "rollback",
            self._session.rollback,
        )

        logger.debug("Transaction rolled back successfully")

    async def _execute_db_operation(self, operation: str, coro, *args, **kwargs):
        """Generic wrapper for database operations with error handling"""
        try:
            return await coro(*args, **kwargs)
        except OperationalError as e:
            logger.exception(f"Database connection error during {operation}")
            raise DatabaseConnectionError(f"Failed to connect to database: {e}") from e
        except TimeoutError as e:
            logger.exception(f"Database timeout during {operation}")
            raise DatabaseTimeoutError(f"Database operation timed out: {e}") from e
        except SQLAlchemyError as e:
            logger.exception(f"Database error during {operation}")
            raise DatabaseOperationError(f"Database operation failed: {e}") from e
