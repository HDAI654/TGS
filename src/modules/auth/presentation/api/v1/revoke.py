import logging
from fastapi import APIRouter, Depends, HTTPException, Request, Path, status, Header
from pydantic import BaseModel

from src.modules.auth.application.revoke import RevokeService
from src.modules.auth.presentation.api.v1.dependencies import get_revoke_service
from src.modules.auth.presentation.api.v1.utils import extract_device
from src.modules.auth.exceptions import (
    InvalidAuthTokenError,
    DeviceMismatchError,
    SessionNotFoundError,
    PermissionDenied,
    CacheError,
)
from src.modules.auth.presentation.api.v1.rate_limiter import rate_limit

logger = logging.getLogger(__name__)

router = APIRouter()

RATE_LIMIT_MAX_REQUESTS = 20


class RevokeResponse(BaseModel):
    message: str


@router.delete("/sessions/{session_id}", response_model=RevokeResponse)
@rate_limit(max_requests=RATE_LIMIT_MAX_REQUESTS, window="min", key_prefix="revoke")
async def revoke_session(
    request: Request,
    session_id: str = Path(..., description="The session ID to revoke"),
    authorization: str = Header(..., alias="Authorization"),
    service: RevokeService = Depends(get_revoke_service),
):
    logger.info("Revoke session endpoint started: session_id=%s", session_id)
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid token format")
    access_token = authorization.split(" ")[1]
    device = extract_device(request)

    try:
        await service.execute(
            access_token=access_token,
            session_id=session_id,
            current_device=device,
        )
    except (InvalidAuthTokenError, DeviceMismatchError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    except SessionNotFoundError as e:
        if e.context and e.context == "current":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionDenied:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
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

    logger.info("Session revoked successfully: session_id=%s", session_id)
    return RevokeResponse(message=f"Session {session_id} revoked successfully")
