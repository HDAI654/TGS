import strawberry
import logging
from strawberry.scalars import JSON
from src.modules.channels.presentation.graphql.v1.country.types import CountryType
from src.modules.channels.domain.ports.unit_of_work_interface import IUnitOfWork
from src.modules.channels.application.get_country import GetCountryService
from src.modules.channels.application.search_country import SearchCountryService
from src.modules.channels.presentation.graphql.v1.error_handler import error_handler
from src.modules.channels.exceptions import CountryNotFoundError, InvalidFieldError
from src.modules.channels.presentation.graphql.v1.error_code import ErrorCodes

logger = logging.getLogger(__name__)


@strawberry.type
class CountryQuery:
    @strawberry.field
    @error_handler(
        "get_country",
        logger,
        {
            CountryNotFoundError: (
                None,
                ErrorCodes.COUNTRY_NOT_FOUND,
                404,
            )
        },
    )
    async def country(
        self,
        country_code: str,
        info: strawberry.Info,
    ) -> CountryType:
        logger.info("GraphQL: Getting country: country_code=%s", country_code)
        uow: IUnitOfWork = info.context.get("uow")
        service = GetCountryService(uow)
        entity = await service.execute(country_code)
        return CountryType.from_entity(entity)

    @strawberry.field
    @error_handler(
        "search_countries",
        logger,
        {
            InvalidFieldError: (
                None,
                ErrorCodes.INVALID_FIELD_ERROR,
                404,
            )
        },
    )
    async def countries(
        self,
        info: strawberry.Info,
        filters: JSON | None = None,
    ) -> list[CountryType]:
        logger.info("GraphQL: Searching countries: filters=%s", filters)
        uow: IUnitOfWork = info.context.get("uow")
        service = SearchCountryService(uow)
        results = await service.execute(filters or {})
        return [CountryType.from_entity(r) for r in results]
