import strawberry
import logging
from src.channel_app.presentation.graphql.v1.country.types import CountryType
from src.channel_app.domain.ports.unit_of_work_interface import IUnitOfWork
from src.channel_app.application.create_country import CreateCountryService
from src.channel_app.application.edit_country import EditCountryService
from src.channel_app.application.delete_country import DeleteCountryService

logger = logging.getLogger(__name__)


@strawberry.type
class CountryMutation:
    @strawberry.mutation
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
        return CountryType.from_entity(entity)

    @strawberry.mutation
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
