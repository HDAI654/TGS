from fastapi import APIRouter
from src.modules.channels.presentation.api.v1.sync_all import (
    router as sync_all_router,
)
from src.modules.channels.presentation.api.v1.sync_channels import (
    router as sync_channels_router,
)
from src.modules.channels.presentation.api.v1.sync_countries import (
    router as sync_countries_router,
)

router = APIRouter(
    prefix="/api/v1/admin",
    tags=["Authentication"],
)

router.include_router(sync_all_router)
router.include_router(sync_channels_router)
router.include_router(sync_countries_router)
