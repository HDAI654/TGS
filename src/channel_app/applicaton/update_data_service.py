import logging
from src.channel_app.domain.ports.unit_of_work_interface import IUnitOfWork
from src.channel_app.domain.ports.crawler_interface import ICrawler
from src.channel_app.domain.value_objects.country_code import CountryCode
from src.core.exceptions import ExtractTimeOut, CountryChannelsExtractFaild

logger = logging.getLogger(__name__)


class UpdateDataService:
    def __init__(
        self,
        uow: IUnitOfWork,
        crawler: ICrawler,
    ):
        self.uow = uow
        self.crawler = crawler

    async def execute(self):
        logger.info("Updating countries and channels")

        # Get all current countries from DB
        existing_codes = {c.value for c in await self.uow.country.get_country_codes()}

        # Extract all countries with crawler
        extracted_countries = await self.crawler.extract_countries()
        extracted_codes = set(extracted_countries.keys())

        to_add = extracted_codes - existing_codes
        to_delete = existing_codes - extracted_codes
        to_update = existing_codes & extracted_codes

        # Exctract channels of country
        countries_without_channel = []
        for country in extracted_countries.values():
            try:
                channels = await self.crawler.extract_channels(country.country_code)
            except ExtractTimeOut:
                continue
            except CountryChannelsExtractFaild:
                countries_without_channel.append(country.country_code)
