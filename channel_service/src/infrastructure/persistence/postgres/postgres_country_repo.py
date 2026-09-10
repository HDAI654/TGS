"""SQLAlchemy implementation for country repository interface."""

import logging
from sqlalchemy import func, or_, select, exists
from sqlalchemy.exc import (
    IntegrityError,
    OperationalError,
    SQLAlchemyError,
    TimeoutError,
)
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.entities.country import Country
from src.domain.ports.country_repository import CountryRepository
from src.exceptions.infrastructure import (
    DatabaseConnectionError,
    DatabaseOperationError,
    DatabaseTimeoutError,
)
from src.infrastructure.persistence.mappers import to_country
from src.infrastructure.persistence.search import search_pattern
from src.infrastructure.persistence.models import (
    CountryModel,
)

logger = logging.getLogger(__name__)


class SQLAlchemyCountryRepository(CountryRepository):
    """Read-only SQLAlchemy adapter for countries."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, country_code: str) -> Country | None:
        logger.debug("Fetching country by code: code=%s", country_code)
        result = await self._execute_db_operation(
            "get_country_by_id",
            self._session.execute,
            select(CountryModel).where(CountryModel.country_code == country_code),
        )

        row = result.scalar_one_or_none()
        country = to_country(row) if row else None

        if country:
            logger.debug(
                "Country found: code=%s name=%s", country_code, country.country_name
            )
        else:
            logger.debug("Country not found: code=%s", country_code)

        return country

    async def get_all(self) -> list[Country]:
        logger.debug("Fetching all countries")
        result = await self._execute_db_operation(
            "get_all_countries",
            self._session.execute,
            select(CountryModel).order_by(CountryModel.country_code),
        )

        countries = [to_country(row) for row in result.scalars().all()]
        logger.debug("Retrieved %d countries", len(countries))
        return countries

    async def search(
        self, text: str, limit: int, offset: int
    ) -> tuple[list[Country], int]:
        logger.debug(
            "Searching countries: text='%s', limit=%d, offset=%d", text, limit, offset
        )
        pattern = search_pattern(text)
        filters = [
            func.lower(CountryModel.country_code).like(pattern, escape="\\"),
            func.lower(CountryModel.country_name).like(pattern, escape="\\"),
            func.lower(CountryModel.timezone).like(pattern, escape="\\"),
        ]

        # Count query
        count_result = await self._execute_db_operation(
            "count_search_countries",
            self._session.execute,
            select(func.count(CountryModel.country_code))
            .select_from(CountryModel)
            .where(or_(*filters)),
        )

        total = int(count_result.scalar_one())
        logger.debug("Search found %d total countries matching '%s'", total, text)

        # Main search query
        result = await self._execute_db_operation(
            "search_countries",
            self._session.execute,
            select(CountryModel)
            .where(or_(*filters))
            .order_by(CountryModel.country_code)
            .offset(offset)
            .limit(limit),
        )

        countries = [to_country(row) for row in result.scalars().all()]

        logger.debug(
            "Search returned %d countries (page %d-%d of %d)",
            len(countries),
            offset + 1,
            min(offset + limit, total),
            total,
        )
        return countries, total

    async def exist(self, id: str) -> bool:
        logger.debug("Checking if country exists: code=%s", id)
        result = await self._execute_db_operation(
            "exists_country",
            self._session.execute,
            select(exists().where(CountryModel.country_code == id)),
        )
        res = result.scalar()
        logger.debug("Country exists check completed: code=%s exists=%s", id, res)
        return res

    async def count_countries(self) -> int:
        """Return the total number of countries."""
        logger.debug("Counting all countries")

        result = await self._execute_db_operation(
            "count_countries",
            self._session.execute,
            select(func.count(CountryModel.country_code)),
        )

        total = int(result.scalar_one())
        logger.debug("Total countries: %d", total)

        return total

    async def _execute_db_operation(self, operation: str, coro, *args, **kwargs):
        try:
            logger.debug("Executing database operation: %s", operation)
            return await coro(*args, **kwargs)
        except IntegrityError as e:
            logger.error("Database integrity error during %s: %s", operation, str(e))
            raise DatabaseOperationError(f"Database integrity error: {e}") from e
        except OperationalError as e:
            logger.error("Database connection error during %s: %s", operation, str(e))
            raise DatabaseConnectionError(f"Failed to connect to database: {e}") from e
        except TimeoutError as e:
            logger.error("Database timeout during %s: %s", operation, str(e))
            raise DatabaseTimeoutError(f"Database operation timed out: {e}") from e
        except SQLAlchemyError as e:
            logger.error("Database error during %s: %s", operation, str(e))
            raise DatabaseOperationError(f"Database operation failed: {e}") from e
        except Exception as e:
            logger.exception("Unexpected error during %s", operation)
            raise DatabaseOperationError(f"Unexpected database error: {e}") from e
