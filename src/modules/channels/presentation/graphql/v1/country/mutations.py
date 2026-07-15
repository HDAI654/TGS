import strawberry
import logging
from src.modules.channels.presentation.graphql.v1.country.types import CountryType
from src.modules.channels.domain.ports.unit_of_work_interface import IUnitOfWork
from src.modules.channels.application.create_country import CreateCountryService
from src.modules.channels.application.edit_country import EditCountryService
from src.modules.channels.application.delete_country import DeleteCountryService
from src.modules.channels.presentation.graphql.v1.error_handler import error_handler
from src.modules.channels.exceptions import (
    CountryNotFoundError,
    CountryDuplicateError,
    NoChangesError,
)
from src.modules.channels.presentation.graphql.v1.error_code import ErrorCodes

logger = logging.getLogger(__name__)


@strawberry.type
class CountryMutation:
    @strawberry.mutation
    @error_handler(
        "create_country",
        logger,
        {
            CountryDuplicateError: (None, ErrorCodes.DUPLICATE_COUNTRY, 409),
        },
    )
    async def create_country(
        self,
        country_code: str,
        country_name: str,
        capital: str,
        timezone: str,
        channel_count: int,
        info: strawberry.Info,
    ) -> CountryType:
        logger.info("GraphQL: Creating country: code=%s", country_code)
        uow: IUnitOfWork = info.context.get("uow")
        service = CreateCountryService(uow)
        entity = await service.execute(
            country_code=country_code,
            country_name=country_name,
            capital=capital,
            timezone=timezone,
            channel_count=channel_count,
        )
        logger.info("GraphQL: Creating country finished: code=%s", country_code)
        return CountryType.from_entity(entity)

    @strawberry.mutation
    @error_handler(
        "update_country",
        logger,
        {
            CountryNotFoundError: (
                None,
                ErrorCodes.COUNTRY_NOT_FOUND,
                404,
            ),
            NoChangesError: (
                None,
                ErrorCodes.NO_CHANGES_ERROR,
                400,
            ),
            CountryDuplicateError: (None, ErrorCodes.DUPLICATE_COUNTRY, 409),
        },
    )
    async def update_country(
        self,
        country_code: str,
        info: strawberry.Info,
        new_country_name: str | None = None,
        new_capital: str | None = None,
        new_timezone: str | None = None,
        new_channel_count: int | None = None,
    ) -> bool:
        logger.info("GraphQL: Updating country: code=%s", country_code)
        uow: IUnitOfWork = info.context.get("uow")
        service = EditCountryService(uow)
        await service.execute(
            country_code=country_code,
            new_country_name=new_country_name,
            new_capital=new_capital,
            new_timezone=new_timezone,
            new_channel_count=new_channel_count,
        )
        return True

    @strawberry.mutation
    @error_handler(
        "delete_country",
        logger,
        {
            CountryNotFoundError: (
                None,
                ErrorCodes.COUNTRY_NOT_FOUND,
                404,
            )
        },
    )
    async def delete_country(
        self,
        country_code: str,
        info: strawberry.Info,
    ) -> bool:
        logger.info("GraphQL: Deleting country: code=%s", country_code)
        uow: IUnitOfWork = info.context.get("uow")
        service = DeleteCountryService(uow)
        await service.execute(country_code)
        return True
