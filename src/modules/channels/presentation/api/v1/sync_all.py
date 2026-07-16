import logging
from fastapi import APIRouter, HTTPException, Request, Depends
from src.modules.channels.domain.ports.task_interface import ITask
from src.modules.channels.application.sync_all_data import SyncAllDataService
from src.modules.channels.presentation.api.v1.dependencies import get_sync_all_data_task
from pydantic import BaseModel
from src.modules.channels.presentation.api.v1.auth_checker import auth_check

logger = logging.getLogger(__name__)

router = APIRouter()


class SyncAllResponse(BaseModel):
    status: str
    task_id: str
    message: str


@router.post("/sync/all")
@auth_check(admin_check=True)
async def sync_all(
    request: Request,
    task: ITask = Depends(get_sync_all_data_task),
):
    logger.info("SyncAll endpoint started")
    try:
        service = SyncAllDataService(task)
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
