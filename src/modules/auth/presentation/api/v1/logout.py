import logging
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel

from src.modules.auth.application.logout import LogoutService
from src.modules.auth.presentation.api.v1.dependencies import get_logout_service
from src.modules.auth.presentation.api.v1.utils import extract_device
from src.modules.auth.exceptions import (
    InvalidAuthTokenError,
    DeviceMismatchError,
    SessionNotFoundError,
    CacheError,
)
from src.modules.auth.presentation.api.v1.rate_limiter import rate_limit

logger = logging.getLogger(__name__)

router = APIRouter()

RATE_LIMIT_MAX_REQUESTS = 30


class LogoutRequest(BaseModel):
    access_token: str


class LogoutResponse(BaseModel):
    message: str


@router.post("/logout", response_model=LogoutResponse)
@rate_limit(max_requests=RATE_LIMIT_MAX_REQUESTS, window="min", key_prefix="logout")
async def logout(
    request: Request,
    logout_data: LogoutRequest,
    service: LogoutService = Depends(get_logout_service),
):
    logger.info("Logout endpoint started")
    device = extract_device(request)

    try:
        await service.execute(
            access_token=logout_data.access_token,
            current_device=device,
        )
    except (InvalidAuthTokenError, DeviceMismatchError, SessionNotFoundError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    except CacheError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong. Please try again later.",
        )
    except Exception as e:
        logger.exception("Unexpected error during account deletion")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong. Please try again later.",
        )

    logger.info("Logout completed successfully")
    return LogoutResponse(message="Logged out successfully")
