import logging
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel

from src.modules.auth.application.forget_pass_verify import (
    ForgetPasswordVerificationService,
)
from src.modules.auth.presentation.api.v1.dependencies import (
    get_forget_pass_service,
)
from src.modules.auth.exceptions import (
    InvalidEmailError,
    UserNotFoundError,
    EmailSendingFailedError,
    DatabaseError,
)
from src.modules.auth.presentation.api.v1.rate_limiter import rate_limit

logger = logging.getLogger(__name__)

router = APIRouter()

RATE_LIMIT_MAX_REQUESTS = 5


class ForgetPassRequest(BaseModel):
    email: str


class ForgetPassResponse(BaseModel):
    message: str


@router.post("/forget-password", response_model=ForgetPassResponse)
@rate_limit(
    max_requests=RATE_LIMIT_MAX_REQUESTS, window="hour", key_prefix="forget_pass"
)
async def forget_pass(
    request: Request,
    forget_pass_data: ForgetPassRequest,
    service: ForgetPasswordVerificationService = Depends(get_forget_pass_service),
):
    logger.info("forget-pass endpoint started: email=%s", forget_pass_data.email)

    try:
        await service.execute(email=forget_pass_data.email)
    except InvalidEmailError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid email"
        )
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except EmailSendingFailedError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong. Please try again later.",
        )
    except DatabaseError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong. Please try again later.",
        )
    except Exception as e:
        logger.exception("Unexpected error during send verification")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong. Please try again later.",
        )

    logger.info("forget-pass completed successfully: email=%s", forget_pass_data.email)
    return ForgetPassResponse(message="Reset password email sent successfully")
