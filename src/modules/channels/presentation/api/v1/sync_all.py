import logging
from fastapi import APIRouter, HTTPException, Request
from src.modules.channels.application.sync_all_data import SyncAllDataService
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter()


class SyncAllResponse(BaseModel):
    status: str
    task_id: str
    message: str


@router.post("/sync/all")
async def sync_all(
    request: Request,
):
    logger.info("SyncAll endpoint started")
    try:
        service = SyncAllDataService()
        result = await service.execute()
    except Exception as e:
        logger.exception("Unexpected error during SyncAll endpoint")
        raise HTTPException(
            status_code=500, detail="Something went wrong. Please try again later."
        )

    logger.info("SyncAll finished successfully")
    return SyncAllResponse(
        status=result["status"],
        task_id=result["task_id"],
        message=result["message"],
    )
