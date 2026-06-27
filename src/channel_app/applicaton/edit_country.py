import logging
from src.channel_app.domain.ports.unit_of_work_interface import IUnitOfWork
from src.channel_app.domain.value_objects.country_code import CountryCode
from src.channel_app.domain.value_objects.name import Name
from src.channel_app.domain.value_objects.timezone import Timezone
from src.channel_app.domain.value_objects.count import Count
from src.core.exceptions import InvalidCountryCodeError, CountryNotFoundError

logger = logging.getLogger(__name__)


class EditCountryService:
    def __init__(
        self,
        uow: IUnitOfWork,
    ):
        self.uow = uow

    async def execute(
        self,
        country_code: str,
        new_country_name: str | None = None,
        new_capital: str | None = None,
        new_timezone: str | None = None,
        new_channel_count: int | None = None,
    ) -> None:
        logger.info("Editing country: country_code=%s", country_code)

        # Get country
        try:
            country_code_vo = CountryCode(country_code)
        except InvalidCountryCodeError:
            raise CountryNotFoundError(
                f"Country not found: country_code={country_code}"
            )

        # Convert optional parameters to value objects
        new_country_name_vo = (
            Name(new_country_name) if new_country_name is not None else None
        )
        new_capital_vo = Name(new_capital) if new_capital is not None else None
        new_timezone_vo = Timezone(new_timezone) if new_timezone is not None else None
        new_channel_count_vo = (
            Count(new_channel_count) if new_channel_count is not None else None
        )

        await self.uow.countries.update(
            country_code=country_code_vo,
            new_country_name=new_country_name_vo,
            new_capital=new_capital_vo,
            new_timezone=new_timezone_vo,
            new_channel_count=new_channel_count_vo,
        )
        await self.uow.commit()

        logger.info("Country updated successfully: country_code=%s", country_code)
