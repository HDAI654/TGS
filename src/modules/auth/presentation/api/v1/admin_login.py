import logging
from fastapi import APIRouter, Depends, HTTPException, Request, status, Response
from pydantic import BaseModel

from src.modules.auth.application.admin_login import AdminLoginService
from src.modules.auth.presentation.api.v1.dependencies import get_admin_login_service
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


class AdminLoginRequest(BaseModel):
    email: str
    password: str
    admin_password: str


class AdminLoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    device_id: str


@router.post("/admin-login", response_model=AdminLoginResponse)
@rate_limit(
    max_requests=RATE_LIMIT_MAX_REQUESTS, window="min", key_prefix="admin_login"
)
async def admin_login(
    request: Request,
    response: Response,
    admin_login_data: AdminLoginRequest,
    service: AdminLoginService = Depends(get_admin_login_service),
):
    logger.info("AdminLogin endpoint started: email=%s", admin_login_data.email)
    device = generate_device(response)

    try:
        access_token, refresh_token = await service.execute(
            email=admin_login_data.email,
            password=admin_login_data.password,
            current_device=device,
            admin_password=admin_login_data.admin_password,
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

    logger.info("AdminLogin completed successfully: email=%s", admin_login_data.email)
    return AdminLoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        device_id=device,
    )
