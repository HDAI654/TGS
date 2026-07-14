import logging
from src.modules.channels.domain.ports.task_interface import ITask

logger = logging.getLogger(__name__)


class SyncCountriesService:
    def __init__(self, task: ITask):
        self.task = task

    async def execute(self) -> dict:
        """Trigger country sync in background."""
        logger.info("Country sync requested")

        task = self.task.delay()

        logger.info("Country sync queued successfully: task_id=%s", task.id)

        return {
            "status": "queued",
            "task_id": task.id,
            "message": "Country sync has been queued and will run in the background",
        }
