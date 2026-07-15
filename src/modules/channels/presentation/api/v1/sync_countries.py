import logging
from fastapi import APIRouter, HTTPException, Request
from src.modules.channels.application.sync_countries_data import SyncCountriesService
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
):
    logger.info("SyncCountries endpoint started")
    try:
        service = SyncCountriesService()
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
