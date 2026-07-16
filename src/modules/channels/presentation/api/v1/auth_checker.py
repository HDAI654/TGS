from typing import Callable
from fastapi import Header, HTTPException, status
import jwt
from functools import wraps
from src.modules.core.redis_client import get_redis_client
from src.modules.core.conf import Config
from redis.exceptions import RedisError, ConnectionError, TimeoutError
import logging

logger = logging.getLogger(__name__)


def auth_check(admin_check: bool = False):
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(
            authorization: str = Header(..., alias="Authorization"),
            *args,
            **kwargs,
        ):
            # 1. Validate token format
            if not authorization or not authorization.startswith("Bearer "):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token format. Use: Bearer <token>",
                )

            token = authorization.split(" ")[1]

            # 2. Decode and validate JWT
            try:
                payload = jwt.decode(
                    token,
                    Config.AUTH_TOKEN_PUBLIC_KEY,
                    algorithms=[Config.AUTH_TOKEN_ALGORITHM],
                )
            except jwt.ExpiredSignatureError:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has expired",
                )
            except jwt.InvalidTokenError:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or malformed token",
                )
            except Exception as e:
                logger.exception("Unexpected error during token decode")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Something went wrong. Please try again later.",
                )

            # 3. Validate session ID exists
            if "sid" not in payload:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token: missing session ID",
                )

            # 4. Check session in Redis
            try:
                client = get_redis_client()
                session_data = await client.hgetall(payload["sid"])
            except (RedisError, ConnectionError, TimeoutError) as e:
                logger.exception("Redis error during authentication")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Something went wrong. Please try again later.",
                )

            if not session_data or not session_data.get("user_id"):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Session not found or expired",
                )

            # 5. Admin check
            if admin_check:
                role = payload.get("role", "user")
                if role.strip().lower() != "admin":
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Permission denied: Admin role required",
                    )

            return await func(*args, **kwargs)

        return wrapper

    return decorator
