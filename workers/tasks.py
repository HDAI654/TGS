import logging
from celery import shared_task
from workers.core.context import get_crawler, get_uow
from workers.core.exceptions import DatabaseError, CrawlerError

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    max_retries=3,
    name="update_countries",
    time_limit=180,
    soft_time_limit=150,
)
async def update_countries(self):
    logger.info(
        "Task: update_countries started (attempt %s/%s)", 
        self.request.retries + 1, 
        self.max_retries + 1,
    )
    try:
        crawler = get_crawler()

        # Extract countries
        countries = await crawler.extract_all_countries()

        # Update them in DB
        async with get_uow() as uow:
            await uow.repo.upsert_batch_countries(countries)
            await uow.commit()
        logger.info(
            "Task: update_countries finished successfully (attempt %s/%s)", 
            self.request.retries + 1, 
            self.max_retries + 1,
        )
    except (DatabaseError, CrawlerError) as e:
        logger.exception(
            "Task: update_countries failed (attempt %s/%s)",
            self.request.retries + 1,
            self.max_retries + 1,
        )
        self.retry(exc=e, countdown=60)
        
    except Exception as e:
        logger.exception(
            "Task: update_countries unexpected error (attempt %s/%s)",
            self.request.retries + 1,
            self.max_retries + 1,
        )
        self.retry(exc=e, countdown=60)


@shared_task(
    bind=True,
    max_retries=3,
    name="update_channels",
    time_limit=240,
    soft_time_limit=205,
)
async def update_channels(self):
    logger.info(
        "Task: update_channels started (attempt %s/%s)", 
        self.request.retries + 1, 
        self.max_retries + 1,
    )
    try:
        crawler = get_crawler()

        # Extract channels
        channels_and_urls = await crawler.extract_all_channels()

        # Update them in DB
        async with get_uow() as uow:
            await uow.repo.upsert_batch_channels(channels_and_urls)
            await uow.commit()
        logger.info(
            "Task: update_channels finished successfully (attempt %s/%s)", 
            self.request.retries + 1, 
            self.max_retries + 1,
        )
    except (DatabaseError, CrawlerError) as e:
        logger.exception(
            "Task: update_channels failed (attempt %s/%s)",
            self.request.retries + 1,
            self.max_retries + 1,
        )
        self.retry(exc=e, countdown=60)
        
    except Exception as e:
        logger.exception(
            "Task: update_channels unexpected error (attempt %s/%s)",
            self.request.retries + 1,
            self.max_retries + 1,
        )
        self.retry(exc=e, countdown=60)


@shared_task(
    bind=True, max_retries=3, name="update_all", time_limit=420, soft_time_limit=400
)
async def update_all(self):
    logger.info(
        "Task: update_all started (attempt %s/%s)", 
        self.request.retries + 1, 
        self.max_retries + 1,
    )
    try:
        crawler = get_crawler()

        # Extract countries
        countries = await crawler.extract_all_countries()

        # Extract channels
        channels_and_urls = await crawler.extract_all_channels()

        # Update them in DB
        async with get_uow() as uow:
            await uow.repo.upsert_batch_countries(countries)
            await uow.repo.upsert_batch_channels(channels_and_urls)
            await uow.commit()
        logger.info(
            "Task: update_all finished successfully (attempt %s/%s)", 
            self.request.retries + 1, 
            self.max_retries + 1,
        )
    except (DatabaseError, CrawlerError) as e:
        logger.exception(
            "Task: update_all failed (attempt %s/%s)",
            self.request.retries + 1,
            self.max_retries + 1,
        )
        self.retry(exc=e, countdown=60)
        
    except Exception as e:
        logger.exception(
            "Task: update_all unexpected error (attempt %s/%s)",
            self.request.retries + 1,
            self.max_retries + 1,
        )
        self.retry(exc=e, countdown=60)