import logging
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update, select, delete, and_, exists, func
from sqlalchemy.dialects.postgresql import insert
from src.modules.channels.domain.entities.country import CountryEntity
from src.modules.channels.domain.value_objects.country_code import CountryCode
from src.modules.channels.domain.value_objects.name import Name
from src.modules.channels.domain.value_objects.timezone import Timezone
from src.modules.channels.domain.value_objects.count import Count
from src.modules.channels.infrastructure.persistence.models import CountryModel
from sqlalchemy.exc import (
    IntegrityError,
    OperationalError,
    TimeoutError,
    SQLAlchemyError,
)
from src.modules.channels.exceptions import (
    CountryNotFoundError,
    CountryDuplicateError,
    NoChangesError,
    InvalidFieldError,
    DatabaseOperationError,
    DatabaseConnectionError,
    DatabaseTimeoutError,
)

logger = logging.getLogger(__name__)


class SQLAL_CountryRepository:
    """SQLAlchemy Repository for Country entities."""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def add(self, country: CountryEntity) -> None:
        logger.info(
            "Adding country: country_code=%s, name=%s",
            country.country_code.value,
            country.country_name.value,
        )

        country_model = CountryModel(
            country_code=country.country_code.value,
            country_name=country.country_name.value,
            capital=country.capital.value,
            timezone=country.timezone.value,
            has_channels=country.has_channels.value,
            channel_count=country.channel_count.value,
        )

        self._session.add(country_model)
        await self._execute_db_operation("add_country", self._session.flush)

        logger.info(
            "Country added successfully: country_code=%s", country.country_code.value
        )

    async def update(
        self,
        country_code: CountryCode,
        new_country_name: Name | None = None,
        new_capital: Name | None = None,
        new_timezone: Timezone | None = None,
        new_channel_count: Count | None = None,
    ) -> None:
        logger.info(
            "Updating country: country_code=%s",
            country_code.value,
        )

        update_data = {}
        if new_country_name is not None and isinstance(new_country_name, Name):
            update_data["country_name"] = new_country_name.value
        if new_capital is not None and isinstance(new_capital, Name):
            update_data["capital"] = new_capital.value
        if new_timezone is not None and isinstance(new_timezone, Timezone):
            update_data["timezone"] = new_timezone.value
        if new_channel_count is not None and isinstance(new_channel_count, Count):
            update_data["channel_count"] = new_channel_count.value

        if not update_data:
            logger.debug("No changes provided")
            raise NoChangesError("No non-null changes provided.")

        result = await self._execute_db_operation(
            "update_country",
            self._session.execute,
            update(CountryModel)
            .where(CountryModel.country_code == country_code.value)
            .values(**update_data)
            .returning(CountryModel.country_code),
        )

        updated_id = result.scalar_one_or_none()
        if updated_id is None:
            logger.debug("Country not found: country_code=%s", country_code.value)
            raise CountryNotFoundError(
                f"Country with code {country_code.value!r} not found"
            )

        await self._execute_db_operation("update_country", self._session.flush)

        logger.info("Country updated successfully: country_code=%s", country_code.value)

    async def delete(self, country_code: CountryCode) -> None:
        logger.info(
            "Deleting country: country_code=%s",
            country_code.value,
        )
        result = await self._execute_db_operation(
            "delete_country",
            self._session.execute,
            delete(CountryModel).where(CountryModel.country_code == country_code.value),
        )

        if result.rowcount == 0:
            logger.debug("Country not found: country_code=%s", country_code.value)
            raise CountryNotFoundError(
                f"Country with code {country_code.value!r} not found"
            )

        await self._execute_db_operation("delete_country", self._session.flush)

        logger.info("Country deleted successfully: country_code=%s", country_code.value)

    async def get_by_code(self, country_code: CountryCode) -> CountryEntity:
        logger.info("Getting country by code: country_code=%s", country_code.value)

        result = await self._execute_db_operation(
            "get_country_by_code",
            self._session.execute,
            select(CountryModel).where(CountryModel.country_code == country_code.value),
        )
        country_row = result.scalar_one_or_none()

        if country_row:
            logger.info("Country found: country_code=%s", country_code.value)
            return self._to_entity(country_row)

        logger.debug("Country not found: country_code=%s", country_code.value)
        raise CountryNotFoundError(
            f"Country with code {country_code.value!r} not found"
        )

    async def get_country_codes(self) -> list[CountryCode]:
        logger.info("Getting country codes")

        result = await self._execute_db_operation(
            "get_country_codes",
            self._session.execute,
            select(CountryModel.country_code),
        )

        codes = result.scalars().all()

        country_codes = [CountryCode(code) for code in codes]

        logger.info("%s country codes found", len(country_codes))
        return country_codes

    async def search(self, filters: dict[str, Any]) -> list[CountryEntity]:
        logger.info("Searching countries: filters=%s", filters)

        # Validate fields and filters against entity schema
        valid_fields = set(CountryEntity.FIELD_TYPE_MAP.keys())

        if filters and not set(filters.keys()).issubset(valid_fields):
            raise InvalidFieldError(
                f"Invalid filter keys: {set(filters.keys()) - valid_fields}"
            )

        # Map field names to model columns
        field_to_column = {
            "country_code": CountryModel.country_code,
            "country_name": CountryModel.country_name,
            "capital": CountryModel.capital,
            "timezone": CountryModel.timezone,
            "has_channels": CountryModel.has_channels,
            "channel_count": CountryModel.channel_count,
        }

        query = select(CountryModel)

        # ========== APPLY FILTERS ==========
        conditions = []
        for key, value in filters.items():
            if key not in field_to_column:
                continue
            column = field_to_column[key]

            if key == "country_code":
                conditions.append(column == value)
            elif key in ["country_name", "capital", "timezone"]:
                conditions.append(column.contains(value))
            elif key == "has_channels":
                conditions.append(column == value)
            elif key == "channel_count":
                if isinstance(value, dict):
                    if "min" in value:
                        conditions.append(column >= value["min"])
                    if "max" in value:
                        conditions.append(column <= value["max"])
                else:
                    conditions.append(column == value)

        if conditions:
            query = query.where(and_(*conditions))

        # Execute query
        result = await self._execute_db_operation(
            "search_country", self._session.execute, query
        )

        models = result.scalars().all()
        countries = [
            CountryEntity.create(
                country_code=model.country_code,
                country_name=model.country_name,
                capital=model.capital,
                timezone=model.timezone,
                channel_count=model.channel_count,
            )
            for model in models
        ]

        logger.info("Found %s countries", len(countries))
        return countries

    async def exists_by_code(self, country_code: CountryCode) -> bool:
        result = await self._execute_db_operation(
            "exists_country_by_code",
            self._session.execute,
            select(exists().where(CountryModel.country_code == country_code.value)),
        )
        return result.scalar()

    async def upsert_batch(self, countries: list[CountryEntity]) -> None:
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

    def _to_entity(self, country_model: CountryModel) -> CountryEntity:
        return CountryEntity.create(
            country_code=country_model.country_code,
            country_name=country_model.country_name,
            capital=country_model.capital,
            timezone=country_model.timezone,
            channel_count=country_model.channel_count,
        )

    async def _execute_db_operation(self, operation: str, coro, *args, **kwargs):
        try:
            return await coro(*args, **kwargs)
        except IntegrityError as e:
            error_msg = str(e).lower()
            if "duplicate key" in error_msg or "unique constraint" in error_msg:
                raise CountryDuplicateError(
                    f"Another country with same unique field already exists"
                )
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
