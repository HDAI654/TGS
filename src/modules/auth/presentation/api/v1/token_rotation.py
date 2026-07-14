import logging
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel

from src.modules.auth.application.token_rotation import TokenRotationService
from src.modules.auth.presentation.api.v1.dependencies import get_token_rotation_service
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


class TokenRotationRequest(BaseModel):
    refresh_token: str


class TokenRotationResponse(BaseModel):
    access_token: str
    refresh_token: str | None = None


@router.post("/token/refresh", response_model=TokenRotationResponse)
@rate_limit(
    max_requests=RATE_LIMIT_MAX_REQUESTS, window="min", key_prefix="token_rotation"
)
async def refresh_tokens(
    request: Request,
    data: TokenRotationRequest,
    service: TokenRotationService = Depends(get_token_rotation_service),
):
    logger.info("Token rotation endpoint started")
    device = extract_device(request)

    try:
        access_token, refresh_token = await service.execute(
            refresh_token=data.refresh_token,
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
        logger.exception("Unexpected error during token rotation")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong. Please try again later.",
        )

    logger.info("Token rotation completed successfully")
    return TokenRotationResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )
