import logging
from workers.tasks import update_countries

logger = logging.getLogger(__name__)


class SyncCountriesService:
    async def execute(self) -> dict:
        """Trigger country sync in background."""
        logger.info("Country sync requested")

        task = update_countries.delay()

        logger.info("Country sync queued successfully: task_id=%s", task.id)

        return {
            "status": "queued",
            "task_id": task.id,
            "message": "Country sync has been queued and will run in the background",
        }
