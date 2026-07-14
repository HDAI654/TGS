import logging
from fastapi import APIRouter, Depends, HTTPException, Request, Header, status
from pydantic import BaseModel

from src.modules.auth.application.del_account import DelAccountService
from src.modules.auth.presentation.api.v1.dependencies import get_del_account_service
from src.modules.auth.presentation.api.v1.utils import extract_device
from src.modules.auth.exceptions import (
    DeviceMismatchError,
    InvalidAuthTokenError,
    SessionNotFoundError,
    UserNotFoundError,
    DatabaseError,
    CacheError,
)
from src.modules.auth.presentation.api.v1.rate_limiter import rate_limit

logger = logging.getLogger(__name__)

router = APIRouter()

RATE_LIMIT_MAX_REQUESTS = 3


class DelAccountResponse(BaseModel):
    message: str


@router.delete("/account", response_model=DelAccountResponse)
@rate_limit(
    max_requests=RATE_LIMIT_MAX_REQUESTS, window="hour", key_prefix="del_account"
)
async def delete_account(
    request: Request,
    authorization: str = Header(..., alias="Authorization"),
    service: DelAccountService = Depends(get_del_account_service),
):
    logger.info("Delete account endpoint started")
    device = extract_device(request)

    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid token format")

    access_token = authorization.split(" ")[1]

    try:
        await service.execute(
            access_token=access_token,
            current_device=device,
        )
    except (InvalidAuthTokenError, DeviceMismatchError, SessionNotFoundError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
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

    logger.info("Account deleted successfully")
    return DelAccountResponse(message="Account deleted successfully")
