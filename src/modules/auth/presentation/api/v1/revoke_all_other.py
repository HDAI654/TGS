import logging
from fastapi import APIRouter, Depends, HTTPException, Request, status, Header
from pydantic import BaseModel

from src.modules.auth.application.revoke_all_other import RevokeAllOtherSessionsService
from src.modules.auth.presentation.api.v1.dependencies import (
    get_revoke_all_other_service,
)
from src.modules.auth.presentation.api.v1.utils import extract_device
from src.modules.auth.exceptions import (
    InvalidAuthTokenError,
    SessionNotFoundError,
    DeviceMismatchError,
    CacheError,
)
from src.modules.auth.presentation.api.v1.rate_limiter import rate_limit

logger = logging.getLogger(__name__)

router = APIRouter()

RATE_LIMIT_MAX_REQUESTS = 10


class RevokeAllOtherResponse(BaseModel):
    message: str


@router.delete("/sessions", response_model=RevokeAllOtherResponse)
@rate_limit(
    max_requests=RATE_LIMIT_MAX_REQUESTS, window="min", key_prefix="revoke_all_other"
)
async def revoke_all_other_sessions(
    request: Request,
    authorization: str = Header(..., alias="Authorization"),
    service: RevokeAllOtherSessionsService = Depends(get_revoke_all_other_service),
):
    logger.info("Revoke all other sessions endpoint started")
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid token format")
    access_token = authorization.split(" ")[1]
    device = extract_device(request)

    try:
        await service.execute(
            access_token=access_token,
            current_device=device,
        )
    except (InvalidAuthTokenError, SessionNotFoundError, DeviceMismatchError):
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

    logger.info("All other sessions revoked successfully")
    return RevokeAllOtherResponse(message="All other sessions revoked successfully")
