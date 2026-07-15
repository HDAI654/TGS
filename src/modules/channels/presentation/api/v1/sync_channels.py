import logging
from fastapi import APIRouter, HTTPException, Request, Depends
from src.modules.channels.domain.ports.task_interface import ITask
from src.modules.channels.application.sync_channels_data import SyncChannelsService
from src.modules.channels.presentation.api.v1.dependencies import get_sync_channels_task
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter()


class SyncChannelsResponse(BaseModel):
    status: str
    task_id: str
    message: str


@router.post("/sync/channels")
async def sync_channels(
    request: Request,
    task: ITask = Depends(get_sync_channels_task),
):
    logger.info("SyncChannels endpoint started")
    try:
        service = SyncChannelsService(task)
        result = await service.execute()
    except Exception as e:
        logger.exception("Unexpected error during SyncChannels endpoint")
        raise HTTPException(
            status_code=500, detail="Something went wrong. Please try again later."
        )

    logger.info("SyncChannels finished successfully")
    return SyncChannelsResponse(
        status=result["status"],
        task_id=result["task_id"],
        message=result["message"],
    )
