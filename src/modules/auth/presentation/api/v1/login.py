import logging
from fastapi import APIRouter, Depends, HTTPException, Request, status, Response
from pydantic import BaseModel

from src.modules.auth.application.login import LoginService
from src.modules.auth.presentation.api.v1.dependencies import get_login_service
from src.modules.auth.presentation.api.v1.utils import generate_device
from src.modules.auth.exceptions import (
    UserNotFoundError,
    InvalidEmailOrPassword,
    DatabaseError,
    CacheError,
)
from src.modules.auth.presentation.api.v1.rate_limiter import rate_limit

logger = logging.getLogger(__name__)

router = APIRouter()

RATE_LIMIT_MAX_REQUESTS = 10


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    device_id: str


@router.post("/login", response_model=LoginResponse)
@rate_limit(max_requests=RATE_LIMIT_MAX_REQUESTS, window="min", key_prefix="login")
async def login(
    request: Request,
    response: Response,
    login_data: LoginRequest,
    service: LoginService = Depends(get_login_service),
):
    logger.info("Login endpoint started: email=%s", login_data.email)
    device = generate_device(response)

    try:
        access_token, refresh_token = await service.execute(
            email=login_data.email,
            password=login_data.password,
            current_device=device,
        )
    except (UserNotFoundError, InvalidEmailOrPassword):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )
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

    logger.info("Login completed successfully: email=%s", login_data.email)
    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        device_id=device,
    )
