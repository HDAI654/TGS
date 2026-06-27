import logging
from src.channel_app.domain.ports.unit_of_work_interface import IUnitOfWork
from src.channel_app.domain.entities.country import CountryEntity
from src.channel_app.domain.factories.country_factory import CountryFactory

logger = logging.getLogger(__name__)


class CreateCountryService:
    def __init__(
        self,
        uow: IUnitOfWork,
    ):
        self.uow = uow

    async def execute(
        self,
        country_code: str,
        country_name: str,
        capital: str,
        timezone: str,
        channel_count: int,
        **kwargs,
    ) -> CountryEntity:
        logger.info(
            "Creating country: country_code=%s, country_name=%s",
            country_code,
            country_name,
        )

        # Create country entity
        country = CountryFactory.create(
            country_code=country_code,
            country_name=country_name,
            capital=capital,
            timezone=timezone,
            channel_count=channel_count,
        )

        await self.uow.countries.add(country)
        await self.uow.commit()

        logger.info("Country created successfully: country_id=%s", country.id.value)
        return country
