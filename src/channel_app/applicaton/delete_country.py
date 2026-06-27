import logging
from src.channel_app.domain.ports.unit_of_work_interface import IUnitOfWork
from src.channel_app.domain.value_objects.country_code import CountryCode
from src.core.exceptions import InvalidCountryCodeError, CountryNotFoundError

logger = logging.getLogger(__name__)


class DeleteCountryService:
    def __init__(
        self,
        uow: IUnitOfWork,
    ):
        self.uow = uow

    async def execute(self, country_code: str) -> None:
        logger.info("Deleting country: country_code=%s", country_code)

        # Get country
        try:
            country_code_vo = CountryCode(country_code)
        except InvalidCountryCodeError:
            raise CountryNotFoundError(
                f"Country not found: country_code={country_code}"
            )

        await self.uow.countries.delete(country_code_vo)
        await self.uow.commit()

        logger.info("Country deleted successfully: country_code=%s", country_code)
