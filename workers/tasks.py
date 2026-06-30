import logging
from celery import shared_task
from workers.context import get_crawler, get_repo

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, name="update_countries")
async def update_countries(self):
    crawler = get_crawler()
    repo = get_repo()

    # Extract countries
    countries = await crawler.extract_all_countries()

    # Update them in DB
    repo.upsert_batch_countries(countries)


@shared_task(bind=True, max_retries=3, name="update_channels")
async def update_channels(self):
    crawler = get_crawler()
    repo = get_repo()

    # Extract channels
    channels_and_urls = await crawler.extract_all_channels()

    # Update them in DB
    repo.upsert_batch_channels(channels_and_urls)


@shared_task(bind=True, max_retries=3, name="update_all")
async def update_all(self):
    crawler = get_crawler()
    repo = get_repo()

    # Extract countries
    countries = await crawler.extract_all_countries()

    # Extract channels
    channels_and_urls = await crawler.extract_all_channels()

    # Update them in DB
    repo.upsert_batch_countries(countries)
    repo.upsert_batch_channels(channels_and_urls)
