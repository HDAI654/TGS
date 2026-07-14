import logging
from fastapi import APIRouter, Depends, HTTPException, Request, status, Response
from pydantic import BaseModel

from src.modules.auth.application.signup import SignupService
from src.modules.auth.presentation.api.v1.dependencies import get_signup_service
from src.modules.auth.presentation.api.v1.utils import generate_device
from src.modules.auth.exceptions import (
    InvalidVerificationToken,
    WeakPasswordError,
    InvalidPasswordError,
    DatabaseError,
    CacheError,
)
from src.modules.auth.presentation.api.v1.rate_limiter import rate_limit

logger = logging.getLogger(__name__)

router = APIRouter()

RATE_LIMIT_MAX_REQUESTS = 5


class SignupRequest(BaseModel):
    verify_token: str
    password: str


class SignupResponse(BaseModel):
    access_token: str
    refresh_token: str
    message: str
    device_id: str


@router.post("/signup", status_code=201, response_model=SignupResponse)
@rate_limit(max_requests=RATE_LIMIT_MAX_REQUESTS, window="hour", key_prefix="signup")
async def signup(
    request: Request,
    response: Response,
    signup_data: SignupRequest,
    service: SignupService = Depends(get_signup_service),
):
    logger.info("Signup endpoint started")
    device = generate_device(response)

    try:
        access_token, refresh_token = await service.execute(
            verify_token=signup_data.verify_token,
            password=signup_data.password,
            current_device=device,
        )
    except InvalidVerificationToken as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (WeakPasswordError, InvalidPasswordError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except (DatabaseError, CacheError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong. Please try again later.",
        )
    except Exception as e:
        logger.exception("Unexpected error during signup")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong. Please try again later.",
        )

    logger.info("Signup completed successfully")
    return SignupResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        message="User registered successfully",
        device_id=device,
    )
