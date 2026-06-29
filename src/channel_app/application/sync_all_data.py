import logging
from workers.tasks import update_all

logger = logging.getLogger(__name__)


class SyncAllDataService:
    async def execute(self) -> dict:
        """Trigger full data sync (countries + channels) in background."""
        logger.info("Full data sync requested")

        task = update_all.delay()

        logger.info("Full data sync queued successfully: task_id=%s", task.id)

        return {
            "status": "queued",
            "task_id": task.id,
            "message": "Full data sync has been queued and will run in the background",
        }
