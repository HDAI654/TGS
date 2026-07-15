from celery import Celery
from workers.core.conf import Config
from workers.logging_config import setup_logging

setup_logging()

celery_app = Celery(
    Config.APP_NAME,
    broker=Config.REDIS_URL,
    backend=Config.REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_default_retry_delay=60,
    task_max_retries=3,
    worker_concurrency=1,
    worker_prefetch_multiplier=1,
)

celery_app.autodiscover_tasks(["workers"])
