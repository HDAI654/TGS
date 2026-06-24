import logging
from src.channel_app.domain.ports.unit_of_work_interface import IUnitOfWork
from src.channel_app.domain.ports.crawler_interface import ICrawler

logger = logging.getLogger(__name__)


class UpdateChannelsService:
    def __init__(
        self,
        uow: IUnitOfWork,
        crawler: ICrawler,
    ):
        self.uow = uow
        self.crawler = crawler

    async def execute(self):
        logger.info("Updating channels")

        # Get all country codes
        country_codes = await self.uow.countries.get_country_codes()

        # Extract all channels with crawler
        extracted_channels = await self.crawler.extract_all_channels(country_codes)

        logger.info("Extracted %s channels from crawler", len(extracted_channels))

        # Adds new channels & Updates changed channels
        await self.uow.channels.upsert_batch(extracted_channels)

        await self.uow.commit()

        logger.info("Successfully synced %s channels", len(extracted_channels))
