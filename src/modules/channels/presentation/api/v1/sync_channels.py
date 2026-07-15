import logging
from fastapi import APIRouter, HTTPException, Request
from src.modules.channels.application.sync_channels_data import SyncChannelsService
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
):
    logger.info("SyncChannels endpoint started")
    try:
        service = SyncChannelsService()
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
