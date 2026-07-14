import logging
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel

from src.modules.auth.application.reset_password import ResetPasswordService
from src.modules.auth.presentation.api.v1.dependencies import get_reset_pass_service
from src.modules.auth.exceptions import (
    InvalidVerificationToken,
    WeakPasswordError,
    InvalidPasswordError,
    DatabaseError,
)
from src.modules.auth.presentation.api.v1.rate_limiter import rate_limit

logger = logging.getLogger(__name__)

router = APIRouter()

RATE_LIMIT_MAX_REQUESTS = 5


class ResetPassRequest(BaseModel):
    verify_token: str
    new_password: str


class ResetPassResponse(BaseModel):
    message: str


@router.post("/reset-password", response_model=ResetPassResponse)
@rate_limit(
    max_requests=RATE_LIMIT_MAX_REQUESTS, window="hour", key_prefix="reset_pass"
)
async def reset_password(
    request: Request,
    reset_pass_data: ResetPassRequest,
    service: ResetPasswordService = Depends(get_reset_pass_service),
):
    logger.info("Reset password endpoint started")

    try:
        await service.execute(
            verify_token=reset_pass_data.verify_token,
            new_password=reset_pass_data.new_password,
        )
    except InvalidVerificationToken as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (WeakPasswordError, InvalidPasswordError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except DatabaseError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong. Please try again later.",
        )
    except Exception as e:
        logger.exception("Unexpected error during Reset password")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong. Please try again later.",
        )

    logger.info("Reset password completed successfully")
    return ResetPassResponse(
        message="Password reset successfully.",
    )
