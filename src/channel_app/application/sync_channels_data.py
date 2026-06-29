import logging
from workers.tasks import update_channels

logger = logging.getLogger(__name__)


class SyncChannelsService:
    async def execute(self) -> dict:
        """Trigger channel sync in background."""
        logger.info("Channel sync requested")

        task = update_channels.delay()

        logger.info("Channel sync queued successfully: task_id=%s", task.id)

        return {
            "status": "queued",
            "task_id": task.id,
            "message": "Channel sync has been queued and will run in the background",
        }
