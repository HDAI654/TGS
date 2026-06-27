import logging
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update, select, delete, and_, exists, func
from sqlalchemy.dialects.postgresql import insert
from src.channel_app.domain.entities.channel import ChannelEntity
from src.channel_app.domain.entities.url_entity import URLEntity
from src.channel_app.domain.factories.channel_factory import ChannelFactory
from src.channel_app.domain.factories.url_factory import URLFactory
from src.channel_app.domain.value_objects.country_code import CountryCode
from src.channel_app.domain.value_objects.name import Name
from src.channel_app.domain.value_objects.category import Category
from src.channel_app.domain.value_objects.is_geo_blocked import IsGeoBlocked
from src.channel_app.infrastructure.persistence.models import ChannelModel, URLModel
from src.core.id_vo import ID
from sqlalchemy.exc import (
    IntegrityError,
    OperationalError,
    TimeoutError,
    SQLAlchemyError,
)
from src.core.exceptions import (
    ChannelNotFoundError,
    NoChangesError,
    InvalidFieldError,
    DatabaseOperationError,
    DatabaseConnectionError,
    DatabaseTimeoutError,
    URLNotFoundError,
)

logger = logging.getLogger(__name__)


class SQLAL_ChannelRepository:
    """SQLAlchemy Repository for Channel entities."""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def add(self, channel: ChannelEntity) -> None:
        """Create a new channel in the database."""
        logger.info(
            "Adding channel: name=%s, country_code=%s",
            channel.name.value,
            channel.country_code.value,
        )

        channel_model = ChannelModel(
            nano_id=channel.id.value,
            name=channel.name.value,
            category=channel.category.value,
            language=channel.language.value,
            country_code=channel.country_code.value,
            is_geo_blocked=channel.is_geo_blocked.value,
        )

        self._session.add(channel_model)
        await self._execute_db_operation("add_channel", self._session.flush)

        logger.info("Channel added successfully: channel_id=%s", channel.id.value)

    async def update(
        self,
        channel_id: ID,
        new_name: Name | None = None,
        new_category: Category | None = None,
        new_country_code: CountryCode | None = None,
        new_is_geo_blocked: IsGeoBlocked | None = None,
    ) -> None:
        """Update an existing channel in the database."""
        logger.info("Updating channel: channel_id=%s", channel_id.value)

        update_data = {}
        if new_name is not None:
            update_data["name"] = new_name.value
        if new_category is not None:
            update_data["category"] = new_category.value
        if new_country_code is not None:
            update_data["country_code"] = new_country_code.value
        if new_is_geo_blocked is not None:
            update_data["is_geo_blocked"] = new_is_geo_blocked.value

        if not update_data:
            logger.debug("No changes provided")
            raise NoChangesError("No non-null changes provided.")

        result = await self._execute_db_operation(
            "update_channel",
            self._session.execute,
            update(ChannelModel)
            .where(ChannelModel.nano_id == channel_id.value)
            .values(**update_data)
            .returning(ChannelModel.nano_id),
        )

        updated_id = result.scalar_one_or_none()
        if updated_id is None:
            logger.debug("Channel not found: channel_id=%s", channel_id.value)
            raise ChannelNotFoundError(
                f"Channel with id {channel_id.value!r} not found"
            )

        await self._execute_db_operation("update_channel", self._session.flush)

        logger.info("Channel updated successfully: channel_id=%s", channel_id.value)

    async def delete(self, channel_id: ID) -> None:
        """Delete a channel by ID."""
        logger.info("Deleting channel: channel_id=%s", channel_id.value)

        result = await self._execute_db_operation(
            "delete_channel",
            self._session.execute,
            delete(ChannelModel).where(ChannelModel.nano_id == channel_id.value),
        )

        if result.rowcount == 0:
            logger.debug("Channel not found: channel_id=%s", channel_id.value)
            raise ChannelNotFoundError(
                f"Channel with id {channel_id.value!r} not found"
            )

        await self._execute_db_operation("delete_channel", self._session.flush)

        logger.info("Channel deleted successfully: channel_id=%s", channel_id.value)

    async def get_by_id(self, channel_id: ID) -> ChannelEntity:
        """Get a channel by ID."""
        logger.info("Getting channel by id: channel_id=%s", channel_id.value)

        result = await self._execute_db_operation(
            "get_channel_by_id",
            self._session.execute,
            select(ChannelModel).where(ChannelModel.nano_id == channel_id.value),
        )
        channel_row = result.scalar_one_or_none()

        if channel_row:
            logger.info("Channel found: channel_id=%s", channel_id.value)
            return self._to_entity(channel_row)

        logger.debug("Channel not found: channel_id=%s", channel_id.value)
        raise ChannelNotFoundError(f"Channel with id {channel_id.value!r} not found")

    async def search(
        self, fields: list[str], filters: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Search channels by filters and return specified fields."""
        logger.info("Searching channels: fields=%s, filters=%s", fields, filters)

        # Validate fields and filters against entity schema
        valid_fields = set(ChannelEntity.FIELD_TYPE_MAP.keys())

        if fields and not set(fields).issubset(valid_fields):
            raise InvalidFieldError(f"Invalid fields: {set(fields) - valid_fields}")

        if filters and not set(filters.keys()).issubset(valid_fields):
            raise InvalidFieldError(
                f"Invalid filter keys: {set(filters.keys()) - valid_fields}"
            )

        # Map field names to model columns
        field_to_column = {
            "id": ChannelModel.nano_id,
            "name": ChannelModel.name,
            "category": ChannelModel.category,
            "language": ChannelModel.language,
            "country_code": ChannelModel.country_code,
            "is_geo_blocked": ChannelModel.is_geo_blocked,
        }

        # Build query
        if fields:
            # Select only requested columns
            columns_to_select = [
                field_to_column[f] for f in fields if f in field_to_column
            ]
            # Always include id if not already included (needed for reference)
            if "id" not in fields:
                columns_to_select.append(ChannelModel.nano_id)
            query = select(*columns_to_select)
        else:
            # Select all
            query = select(ChannelModel)

        # ========== APPLY FILTERS ==========
        conditions = []
        for key, value in filters.items():
            if key not in field_to_column:
                continue
            column = field_to_column[key]

            if key == "id":
                conditions.append(column == value)
            elif key == "country_code":
                conditions.append(column == value)
            elif key == "language":
                conditions.append(column == value)
            elif key in ["name", "category"]:
                conditions.append(column.contains(value))
            elif key == "is_geo_blocked":
                conditions.append(column == value)

        if conditions:
            query = query.where(and_(*conditions))

        # Execute query
        result = await self._execute_db_operation(
            "search_channel", self._session.execute, query
        )

        countries = []
        if fields:
            rows = result.all()

            # Determine field order in the result
            selected_fields = [f for f in fields if f in field_to_column]
            if "id" not in fields:
                selected_fields.append("id")

            # Convert each row tuple to dict
            for row in rows:
                channel_dict = dict(zip(selected_fields, row))
                countries.append(channel_dict)
        else:
            models = result.scalars().all()
            for model in models:
                channel_dict = {
                    "id": model.nano_id,
                    "name": model.name,
                    "category": model.category,
                    "language": model.language,
                    "country_code": model.country_code,
                    "is_geo_blocked": model.is_geo_blocked,
                    "created_at": (
                        model.created_at.isoformat() if model.created_at else None
                    ),
                    "updated_at": (
                        model.updated_at.isoformat() if model.updated_at else None
                    ),
                }
                countries.append(channel_dict)

        logger.info("Found %s channels", len(countries))
        return countries

    async def exists_by_id(self, channel_id: ID) -> bool:
        """Check if a channel exists by ID."""
        result = await self._execute_db_operation(
            "exists_channel_by_id",
            self._session.execute,
            select(exists().where(ChannelModel.nano_id == channel_id.value)),
        )
        return result.scalar()

    async def upsert_batch(self, channels: list[ChannelEntity]) -> None:
        """Add new channels and update changed channels."""
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

    async def add_new_url(self, channel_id: ID, url: URLEntity) -> None:
        """Add new url to a channel."""
        logger.info("Adding URL to channel: channel_id=%s", channel_id.value)

        url_model = URLModel(
            nano_id=url.id.value,
            channel_id=channel_id.value,
            url=url.url.value,
        )

        self._session.add(url_model)
        await self._execute_db_operation("add_new_url", self._session.flush)

        logger.info(
            "URL added successfully: channel_id=%s, url_id=%s",
            channel_id.value,
            url.id.value,
        )

    async def remove_url(self, url_id: ID) -> None:
        """Remove a url from a channel."""
        logger.info("Removing URL: url_id=%s", url_id.value)

        result = await self._execute_db_operation(
            "remove_url",
            self._session.execute,
            delete(URLModel).where(URLModel.nano_id == url_id.value),
        )

        if result.rowcount == 0:
            logger.debug("URL not found: url_id=%s", url_id.value)
            raise URLNotFoundError(f"URL with id {url_id.value!r} not found")

        await self._execute_db_operation("remove_url", self._session.flush)

        logger.info("URL removed successfully: url_id=%s", url_id.value)

    async def get_urls(self, channel_id: ID) -> list[URLEntity]:
        """Get all URLs for a channel."""
        logger.info("Getting URLs for channel: channel_id=%s", channel_id.value)

        result = await self._execute_db_operation(
            "get_urls",
            self._session.execute,
            select(URLModel).where(URLModel.channel_id == channel_id.value),
        )
        url_rows = result.scalars().all()

        urls = [self._to_url_entity(row) for row in url_rows]

        logger.info(
            "Found %s URLs for channel: channel_id=%s", len(urls), channel_id.value
        )
        return urls

    def _to_entity(self, channel_model: ChannelModel) -> ChannelEntity:
        """Convert ChannelModel to ChannelEntity."""
        return ChannelFactory.create(
            id=channel_model.nano_id,
            name=channel_model.name,
            category=channel_model.category,
            language=channel_model.language,
            country_code=channel_model.country_code,
            is_geo_blocked=channel_model.is_geo_blocked,
        )

    def _to_url_entity(self, url_model: URLModel) -> URLEntity:
        """Convert URLModel to URLEntity."""
        return URLFactory.create(
            id=url_model.nano_id,
            url=url_model.url,
        )

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
