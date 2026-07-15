import logging
from fastapi import APIRouter, HTTPException, Request, Depends
from src.modules.channels.domain.ports.task_interface import ITask
from src.modules.channels.application.sync_countries_data import SyncCountriesService
from src.modules.channels.presentation.api.v1.dependencies import (
    get_sync_countries_task,
)
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter()


class SyncCountriesResponse(BaseModel):
    status: str
    task_id: str
    message: str


@router.post("/sync/countries")
async def sync_countries(
    request: Request,
    task: ITask = Depends(get_sync_countries_task),
):
    logger.info("SyncCountries endpoint started")
    try:
        service = SyncCountriesService(task)
        result = await service.execute()
    except Exception as e:
        logger.exception("Unexpected error during SyncCountries endpoint")
        raise HTTPException(
            status_code=500, detail="Something went wrong. Please try again later."
        )

    logger.info("SyncCountries finished successfully")
    return SyncCountriesResponse(
        status=result["status"],
        task_id=result["task_id"],
        message=result["message"],
    )
