import logging
from src.modules.channels.domain.ports.task_interface import ITask

logger = logging.getLogger(__name__)


class SyncAllDataService:
    def __init__(self, task: ITask):
        self.task = task

    async def execute(self) -> dict:
        """Trigger full data sync (countries + channels) in background."""
        logger.info("Full data sync requested")

        task = self.task.delay()

        logger.info("Full data sync queued successfully: task_id=%s", task.id)

        return {
            "status": "queued",
            "task_id": task.id,
            "message": "Full data sync has been queued and will run in the background",
        }
