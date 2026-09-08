import time

from celery import shared_task


@shared_task
def update_data() -> None:
    """Update categories, countries, and channels data."""
    time.sleep(5) # temporarly