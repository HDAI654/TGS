import uuid
from fastapi import Request, HTTPException, status, Response

COOKIE_NAME = "_device_id"
COOKIE_MAX_AGE = 30 * 24 * 60 * 60


def generate_device(response: Response | None) -> str:
    dev_id = f"dev_{str(uuid.uuid4())}"
    if response and isinstance(response, Response):
        response.set_cookie(
            key=COOKIE_NAME,
            value=dev_id,
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=COOKIE_MAX_AGE,
            path="/",
        )
    return dev_id


def extract_device(
    request: Request,
) -> str:
    # Check header (mobile apps)
    header_device = request.headers.get("X-Device-Id")
    if header_device:
        return header_device[:50]

    # Check cookie (web browsers)
    cookie_device = request.cookies.get(COOKIE_NAME)
    if cookie_device:
        return cookie_device

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Device ID required. Please provide X-Device-Id header or _device_id cookie.",
    )
