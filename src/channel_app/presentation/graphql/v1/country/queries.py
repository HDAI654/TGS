import strawberry
import logging
from strawberry.scalars import JSON
from src.channel_app.presentation.graphql.v1.country.types import CountryType
from src.channel_app.domain.ports.unit_of_work_interface import IUnitOfWork
from src.channel_app.application.get_country import GetCountryService
from src.channel_app.application.search_country import SearchCountryService

logger = logging.getLogger(__name__)


@strawberry.type
class CountryQuery:
    @strawberry.field
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
    async def countries(
        self,
        info: strawberry.Info,
        fields: list[str] | None = None,
        filters: JSON | None = None,
    ) -> list[CountryType]:
        logger.info(
            "GraphQL: Searching countries: fields=%s, filters=%s", fields, filters
        )
        uow: IUnitOfWork = info.context.get("uow")
        service = SearchCountryService(uow)
        results = await service.execute(fields or [], filters or {})
        return [CountryType(**r) for r in results]
