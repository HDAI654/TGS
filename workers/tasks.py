import logging
import asyncio
from workers.core.context import get_crawler, get_uow
from workers.core.exceptions import DatabaseError, CrawlerError
from workers.celery_app import celery_app

logger = logging.getLogger(__name__)

loop = asyncio.new_event_loop()

BATCH_SIZE = 1000


@celery_app.task(
    bind=True,
    max_retries=3,
    name="update_countries",
    time_limit=180,
    soft_time_limit=150,
)
def update_countries(self):
    async def _run():
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
                # Upsert countries
                await uow.repo.upsert_batch_countries(countries)

                # Commit
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

    loop.run_until_complete(_run())


@celery_app.task(
    bind=True,
    max_retries=3,
    name="update_channels",
    time_limit=240,
    soft_time_limit=205,
)
def update_channels(self):
    async def _run():
        logger.info(
            "Task: update_channels started (attempt %s/%s)",
            self.request.retries + 1,
            self.max_retries + 1,
        )
        try:
            crawler = get_crawler()

            # Extract channels
            channels, urls = await crawler.extract_all_channels()
            urls = [(chid, url) for chid, urls in urls.items() for url in urls]

            # Update them in DB
            async with get_uow() as uow:
                # Upsert channels
                for i in range(0, len(channels), BATCH_SIZE):
                    batch = channels[i : i + BATCH_SIZE]
                    await uow.repo.upsert_batch_channels(batch)

                # Upsert urls
                for i in range(0, len(urls), BATCH_SIZE):
                    batch = urls[i : i + BATCH_SIZE]
                    await uow.repo.upsert_batch_urls(batch)

                # Commit
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

    loop.run_until_complete(_run())


@celery_app.task(
    bind=True, max_retries=3, name="update_all", time_limit=420, soft_time_limit=400
)
def update_all(self):
    async def _run():
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
            channels, urls = await crawler.extract_all_channels()
            urls = [(chid, url) for chid, urls in urls.items() for url in urls]

            # Update them in DB
            async with get_uow() as uow:
                # Upsert countries
                await uow.repo.upsert_batch_countries(countries)

                # Upsert channels
                for i in range(0, len(channels), BATCH_SIZE):
                    batch = channels[i : i + BATCH_SIZE]
                    await uow.repo.upsert_batch_channels(batch)

                # Upsert urls
                for i in range(0, len(urls), BATCH_SIZE):
                    batch = urls[i : i + BATCH_SIZE]
                    await uow.repo.upsert_batch_urls(batch)

                # Commit
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

    loop.run_until_complete(_run())
