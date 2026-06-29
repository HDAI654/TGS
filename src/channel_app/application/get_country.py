import logging
from shared.domain.ports.unit_of_work_interface import IUnitOfWork
from shared.domain.entities.country import CountryEntity
from shared.domain.value_objects.country_code import CountryCode
from src.core.exceptions import InvalidCountryCodeError, CountryNotFoundError

logger = logging.getLogger(__name__)


class GetCountryService:
    def __init__(
        self,
        uow: IUnitOfWork,
    ):
        self.uow = uow

    async def execute(self, country_code: str) -> CountryEntity:
        logger.info("Getting country: country_code=%s", country_code)

        # Get country
        try:
            country_code_vo = CountryCode(country_code)
        except InvalidCountryCodeError:
            raise CountryNotFoundError(
                f"Country not found: country_code={country_code}"
            )
        country = await self.uow.countries.get_by_code(country_code_vo)

        logger.info("Country found successfully: country_code=%s", country_code)

        return country
