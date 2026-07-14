import logging
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel

from src.modules.auth.application.set_password import SetPassService
from src.modules.auth.presentation.api.v1.dependencies import get_set_password_service
from src.modules.auth.presentation.api.v1.utils import extract_device
from src.modules.auth.exceptions import (
    InvalidAuthTokenError,
    SessionNotFoundError,
    DeviceMismatchError,
    WeakPasswordError,
    InvalidPasswordError,
    DatabaseError,
    CacheError,
)
from src.modules.auth.presentation.api.v1.rate_limiter import rate_limit

logger = logging.getLogger(__name__)

router = APIRouter()

RATE_LIMIT_MAX_REQUESTS = 5


class SetPasswordRequest(BaseModel):
    access_token: str
    new_password: str


class SetPasswordResponse(BaseModel):
    message: str


@router.put("/password", response_model=SetPasswordResponse)
@rate_limit(
    max_requests=RATE_LIMIT_MAX_REQUESTS, window="hour", key_prefix="set_password"
)
async def set_password(
    request: Request,
    data: SetPasswordRequest,
    service: SetPassService = Depends(get_set_password_service),
):
    logger.info("Set password endpoint started")
    device = extract_device(request)

    try:
        await service.execute(
            access_token=data.access_token,
            new_password=data.new_password,
            current_device=device,
        )
    except (InvalidAuthTokenError, SessionNotFoundError, DeviceMismatchError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    except (InvalidPasswordError, WeakPasswordError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except (DatabaseError, CacheError):
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

    logger.info("Password changed successfully")
    return SetPasswordResponse(message="Password changed successfully")
