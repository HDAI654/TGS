import logging
from src.channel_app.domain.ports.unit_of_work_interface import IUnitOfWork
from src.channel_app.domain.ports.crawler_interface import ICrawler

logger = logging.getLogger(__name__)


class UpdateCountriesService:
    def __init__(
        self,
        uow: IUnitOfWork,
        crawler: ICrawler,
    ):
        self.uow = uow
        self.crawler = crawler

    async def execute(self):
        logger.info("Updating countries")

        # Extract all countries with crawler
        extracted_countries = await self.crawler.extract_all_countries()

        logger.info("Extracted %s countries from crawler", len(extracted_countries))

        # Adds new countries & Updates changed countries
        await self.uow.countries.upsert_batch(extracted_countries)

        await self.uow.commit()

        logger.info("Successfully synced %s countries", len(extracted_countries))
