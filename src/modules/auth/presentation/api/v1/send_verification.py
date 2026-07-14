import logging
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel

from src.modules.auth.application.send_verification import SendVerificationService
from src.modules.auth.presentation.api.v1.dependencies import (
    get_send_verification_service,
)
from src.modules.auth.exceptions import (
    BlockEmail,
    InvalidEmailError,
    EmailSendingFailedError,
    CacheError,
)
from src.modules.auth.presentation.api.v1.rate_limiter import rate_limit

logger = logging.getLogger(__name__)

router = APIRouter()

RATE_LIMIT_MAX_REQUESTS = 5


class SendVerificationRequest(BaseModel):
    email: str


class SendVerificationResponse(BaseModel):
    message: str


@router.post("/verify-email/send", response_model=SendVerificationResponse)
@rate_limit(
    max_requests=RATE_LIMIT_MAX_REQUESTS, window="hour", key_prefix="send_verify"
)
async def send_verification(
    request: Request,
    data: SendVerificationRequest,
    service: SendVerificationService = Depends(get_send_verification_service),
):
    logger.info("Send verification email endpoint started: email=%s", data.email)

    try:
        await service.execute(email=data.email)
    except InvalidEmailError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid email"
        )
    except BlockEmail:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="email is blocked"
        )
    except EmailSendingFailedError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong. Please try again later.",
        )
    except CacheError:
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

    logger.info("Verification email sent successfully: email=%s", data.email)
    return SendVerificationResponse(message="Verification email sent successfully")
