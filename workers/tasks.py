import logging
from workers.celery_app import celery_app
from workers.conf import Config

logger = logging.getLogger(__name__)


async def update_countries(self):
    pass
