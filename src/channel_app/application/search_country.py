import logging
from typing import Any
from src.channel_app.domain.ports.unit_of_work_interface import IUnitOfWork
from src.channel_app.domain.entities.country import CountryEntity
from src.channel_app.domain.factories.country_factory import CountryFactory

logger = logging.getLogger(__name__)


class SearchCountryService:
    def __init__(
        self,
        uow: IUnitOfWork,
    ):
        self.uow = uow

    async def execute(self, filters: dict[str, Any]) -> list[CountryEntity]:
        logger.info("Searching for countries: filters=%s", filters)

        countries = await self.uow.countries.search(
            filters=filters,
        )

        logger.info("Successfully found %s countries", len(countries))

        return countries
