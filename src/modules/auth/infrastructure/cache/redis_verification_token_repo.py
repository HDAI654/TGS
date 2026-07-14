import logging
from src.modules.auth.domain.ports.verification_token_repo_interface import (
    IEmailVerificationTokenRepo,
)
from src.modules.auth.domain.value_objects.email import Email
from src.modules.auth.domain.value_objects.email_verification_token import (
    EmailVerificationToken,
)
from src.modules.core.conf import Config
from src.modules.auth.exceptions import (
    CacheConnectionError,
    CacheTimeoutError,
    CacheOperationError,
)
from redis.asyncio import Redis
from redis.exceptions import RedisError, ConnectionError, TimeoutError

logger = logging.getLogger(__name__)


class RedisEmailVerificationTokenRepo(IEmailVerificationTokenRepo):

    def __init__(self, client: Redis):
        self._client = client

    async def add(
        self,
        token: EmailVerificationToken,
        email: Email,
        token_type: str = "verifyemail",
        ttl_seconds: int = 1440,
    ) -> None:
        key = self._key_creator(token, token_type)

        pipeline = self._client.pipeline()
        pipeline.setex(key, ttl_seconds, email.value)
        await self._execute_redis_operation("add_token", pipeline.execute)

    async def get(
        self,
        token: EmailVerificationToken,
        token_type: str = "verifyemail",
    ) -> Email | None:
        key = self._key_creator(token, token_type)
        email_value = await self._execute_redis_operation(
            "get_token", self._client.get, key
        )
        if email_value is None:
            return None

        if isinstance(email_value, bytes):
            email_value = email_value.decode()

        return Email(email_value)

    async def delete(
        self,
        token: EmailVerificationToken,
        token_type: str = "verifyemail",
    ) -> None:
        key = self._key_creator(token, token_type)

        pipeline = self._client.pipeline()
        pipeline.delete(key)
        await self._execute_redis_operation("delete_token", pipeline.execute)

    def _key_creator(
        self,
        token: EmailVerificationToken,
        token_type: str,
    ) -> str:
        return f"{token_type}:{token.value}"

    async def _execute_redis_operation(self, operation: str, coro, *args, **kwargs):
        """Generic wrapper for Redis operations with error handling"""
        try:
            return await coro(*args, **kwargs)
        except ConnectionError as e:
            logger.exception(f"Failed to connect to Redis during {operation}")
            raise CacheConnectionError(f"Failed to connect to cache: {e}") from e
        except TimeoutError as e:
            logger.exception(f"Redis timeout during {operation}")
            raise CacheTimeoutError(f"Cache operation timed out: {e}") from e
        except RedisError as e:
            logger.exception(f"Redis error during {operation}")
            raise CacheOperationError(f"Cache operation failed: {e}") from e
