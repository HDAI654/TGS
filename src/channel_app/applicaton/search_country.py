import logging
from typing import Any
from src.channel_app.domain.ports.unit_of_work_interface import IUnitOfWork
from src.channel_app.domain.entities.country import CountryEntity

logger = logging.getLogger(__name__)


class SearchCountryService:
    def __init__(
        self,
        uow: IUnitOfWork,
    ):
        self.uow = uow

    async def execute(
        self, fields: list[str], filters: dict[str, Any]
    ) -> list[CountryEntity]:
        logger.info("Searching for countries: fields=%s, filters=%s", fields, filters)

        countries = await self.uow.countries.search(
            fields=fields,
            filters=filters,
        )

        logger.info("Successfully found %s countries", len(countries))

        return countries
