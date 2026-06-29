import logging
from workers.celery_app import celery_app
from workers.conf import Config
from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, name="update_countries")
async def update_countries(self):
    pass


@shared_task(bind=True, max_retries=3, name="update_channels")
async def update_channels(self):
    pass


@shared_task(bind=True, max_retries=3, name="update_all")
async def update_all(self):
    pass
