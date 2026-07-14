import logging
from sqlalchemy.ext.asyncio import AsyncSession
from src.modules.auth.domain.ports.unit_of_work_interface import (
    IUnitOfWork,
)
from src.modules.auth.infrastructure.persistence.sqlal_user_repo import (
    SQLAL_UserRepository,
)
from sqlalchemy.exc import (
    OperationalError,
    TimeoutError,
    SQLAlchemyError,
)
from src.modules.auth.exceptions import (
    DatabaseOperationError,
    DatabaseConnectionError,
    DatabaseTimeoutError,
)

logger = logging.getLogger(__name__)


class SQLAL_UnitOfWork(IUnitOfWork):

    def __init__(self, session: AsyncSession):
        self._session = session

        self.users = SQLAL_UserRepository(session)

    async def commit(self) -> None:
        logger.info("Committing transaction")

        try:
            await self._execute_db_operation(
                "commit",
                self._session.commit,
            )

            logger.info("Transaction committed successfully")

        except Exception:
            logger.warning("Transaction commit failed, rolling back")

            await self._session.rollback()

            logger.info("Transaction rollback completed after commit failure")

            raise

    async def rollback(self) -> None:
        logger.info("Rolling back transaction")

        await self._execute_db_operation(
            "rollback",
            self._session.rollback,
        )

        logger.info("Transaction rolled back successfully")

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
