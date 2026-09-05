import logging
from typing import Tuple

from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError, OperationalError, TimeoutError as SATimeoutError

from src.modules.channels.domain.entities.country import Country
from src.modules.channels.domain.ports.country_repo_interface import CountryRepository
from src.modules.channels.infrastructure.persistence.models import CountryModel
from src.modules.channels.domain.exceptions import CountryNotFoundError
from src.modules.channels.infrastructure.exceptions import (
    DatabaseConnectionError,
    DatabaseTimeoutError,
    DatabaseOperationError,
)

logger = logging.getLogger(__name__)


class PostgresCountryRepository(CountryRepository):
    """PostgreSQL implementation of CountryRepository using async SQLAlchemy."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_code(self, country_code: str) -> Country:
        try:
            stmt = select(CountryModel).where(CountryModel.country_code == country_code)
            result = await self._session.execute(stmt)
            model = result.scalar_one()
        except OperationalError as exc:
            logger.error("Database connection failed for country_code: %s", country_code, exc_info=True)
            raise DatabaseConnectionError("Database connection failed") from exc
        except SATimeoutError as exc:
            logger.error("Database timeout for country_code: %s", country_code, exc_info=True)
            raise DatabaseTimeoutError("Database operation timed out") from exc
        except SQLAlchemyError as exc:
            logger.error("Database operation failed for country_code: %s", country_code, exc_info=True)
            raise DatabaseOperationError("Database operation failed") from exc
        except Exception as exc:
            logger.error("Unexpected database error for country_code: %s", country_code, exc_info=True)
            raise DatabaseOperationError("Unexpected database error") from exc

        if model is None:
            raise CountryNotFoundError(f"Country with code {country_code} not found")

        return self._to_domain(model)

    async def get_all_country_codes(self) -> Tuple[Country, ...]:
        try:
            stmt = select(CountryModel)
            result = await self._session.execute(stmt)
            models = result.scalars().all()
        except OperationalError as exc:
            logger.error("Database connection failed while fetching all countries", exc_info=True)
            raise DatabaseConnectionError("Database connection failed") from exc
        except SATimeoutError as exc:
            logger.error("Database timeout while fetching all countries", exc_info=True)
            raise DatabaseTimeoutError("Database operation timed out") from exc
        except SQLAlchemyError as exc:
            logger.error("Database operation failed while fetching all countries", exc_info=True)
            raise DatabaseOperationError("Database operation failed") from exc
        except Exception as exc:
            logger.error("Unexpected database error while fetching all countries", exc_info=True)
            raise DatabaseOperationError("Unexpected database error") from exc

        return tuple(self._to_domain(m) for m in models)

    async def search(self, text: str, limit: int, offset: int) -> Tuple[Country, ...]:
        logger.debug("Searching countries with text='%s', limit=%d, offset=%d", text, limit, offset)
        try:
            search_pattern = f"%{text.lower()}%"
            stmt = (
                select(CountryModel)
                .where(
                    or_(
                        func.lower(CountryModel.country_name).like(search_pattern),
                        func.lower(CountryModel.country_code).like(search_pattern),
                    )
                )
                .offset(offset)
                .limit(limit)
            )
            result = await self._session.execute(stmt)
            models = result.scalars().all()
        except OperationalError as exc:
            logger.error("Database connection failed during country search", exc_info=True)
            raise DatabaseConnectionError("Database connection failed") from exc
        except SATimeoutError as exc:
            logger.error("Database timeout during country search", exc_info=True)
            raise DatabaseTimeoutError("Database operation timed out") from exc
        except SQLAlchemyError as exc:
            logger.error("Database operation failed during country search", exc_info=True)
            raise DatabaseOperationError("Database operation failed") from exc
        except Exception as exc:
            logger.error("Unexpected database error during country search", exc_info=True)
            raise DatabaseOperationError("Unexpected database error") from exc

        return tuple(self._to_domain(m) for m in models)

    async def exists_by_code(self, country_code: str) -> bool:
        try:
            stmt = select(CountryModel.country_code).where(CountryModel.country_code == country_code)
            result = await self._session.execute(stmt)
            return result.scalar() is not None
        except OperationalError as exc:
            logger.error("Database connection failed for exists check, country_code: %s", country_code, exc_info=True)
            raise DatabaseConnectionError("Database connection failed") from exc
        except SATimeoutError as exc:
            logger.error("Database timeout for exists check, country_code: %s", country_code, exc_info=True)
            raise DatabaseTimeoutError("Database operation timed out") from exc
        except SQLAlchemyError as exc:
            logger.error("Database operation failed for exists check, country_code: %s", country_code, exc_info=True)
            raise DatabaseOperationError("Database operation failed") from exc
        except Exception as exc:
            logger.error("Unexpected database error for exists check, country_code: %s", country_code, exc_info=True)
            raise DatabaseOperationError("Unexpected database error") from exc

    @staticmethod
    def _to_domain(model: CountryModel) -> Country:
        return Country(
            country_code=model.country_code,
            country_name=model.country_name,
            timezone=model.timezone,
            has_channels=model.has_channels,
            channel_count=model.channel_count,
        )