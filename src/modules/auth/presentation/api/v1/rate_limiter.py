import time
from functools import wraps
from typing import Callable
from fastapi import HTTPException, Request, status
from redis.asyncio import Redis
from src.modules.core.redis_client import get_redis_client

_redis_client = None


async def get_redis():
    global _redis_client
    if _redis_client is None:
        _redis_client = await get_redis_client()
    return _redis_client


class RateLimiter:
    TIME_WINDOWS = {
        "sec": 1,
        "min": 60,
        "hour": 3600,
        "day": 86400,
    }

    def __init__(self, max_requests: int, window: str, key_prefix: str = "ratelimit"):
        """
        Args:
            max_requests: Maximum number of requests allowed in the window
            window: Time window ('sec', 'min', 'hour', 'day')
            key_prefix: Prefix for Redis key (e.g., 'auth', 'api')
        """
        self.max_requests = max_requests
        self.window_seconds = self.TIME_WINDOWS.get(window, 60)
        self.key_prefix = key_prefix

    def _get_key(self, identifier: str) -> str:
        """Generate Redis key for rate limiting"""
        return f"{self.key_prefix}:{identifier}"

    async def _get_window_start(self, client: Redis, key: str) -> float:
        """Get current window start time"""
        window_start = await client.get(f"{key}:window")
        if window_start is None:
            window_start = time.time()
            await client.setex(f"{key}:window", self.window_seconds, window_start)
        return float(window_start)

    async def _get_count(self, client: Redis, key: str) -> int:
        """Get current request count"""
        count = await client.get(f"{key}:count")
        return int(count) if count else 0

    async def _increment_count(self, client: Redis, key: str, ttl: int) -> int:
        """Increment request count and return new count"""
        count = await client.incr(f"{key}:count")
        if count == 1:
            await client.expire(f"{key}:count", ttl)
        return count

    async def is_allowed(self, identifier: str) -> bool:
        """
        Check if request is allowed under rate limit
        Returns True if allowed, False if rate limit exceeded
        """
        client = await get_redis()
        key = self._get_key(identifier)
        window_key = f"{key}:window"

        # Get current window start and count
        window_start = await client.get(window_key)
        current_count = await client.get(f"{key}:count")

        current_time = time.time()

        if window_start is None:
            # First request in this window
            await client.setex(window_key, self.window_seconds, current_time)
            await client.setex(f"{key}:count", self.window_seconds, 1)
            return True

        window_start = float(window_start)

        # Check if window has expired
        if current_time - window_start >= self.window_seconds:
            # Reset window
            await client.setex(window_key, self.window_seconds, current_time)
            await client.setex(f"{key}:count", self.window_seconds, 1)
            return True

        # Increment count within existing window
        if current_count is None:
            count = 1
            await client.setex(f"{key}:count", self.window_seconds, count)
        else:
            count = int(current_count) + 1
            await client.incr(f"{key}:count")

        if count > self.max_requests:
            return False

        return True

    async def get_reset_time(self, identifier: str) -> int:
        """Get seconds until rate limit resets"""
        client = await get_redis()
        key = self._get_key(identifier)

        window_start = await client.get(f"{key}:window")
        if window_start is None:
            return 0

        elapsed = time.time() - float(window_start)
        reset_in = int(self.window_seconds - elapsed)
        return max(0, reset_in)


def rate_limit(max_requests: int, window: str, key_prefix: str = "api"):
    """
    Decorator for rate limiting endpoints.

    Usage:
        @rate_limit(10, "min")
        @app.get("/endpoint")
        async def endpoint(request: Request):
            ...

    Headers returned:
        X-RateLimit-Limit: Maximum requests per window
        X-RateLimit-Reset: Seconds until rate limit resets
    """
    key_prefix = "rl_" + key_prefix
    limiter = RateLimiter(max_requests, window, key_prefix)

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract request object from args or kwargs
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            if request is None:
                request = kwargs.get("request")

            if request is None:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Rate limiting requires Request parameter in endpoint",
                )

            # Get client identifier (IP address or API key)
            client_ip = request.client.host if request.client else "unknown"
            identifier = f"{key_prefix}:{client_ip}"

            # Check rate limit
            allowed = await limiter.is_allowed(identifier)

            # Get rate limit headers info
            reset_time = await limiter.get_reset_time(identifier)

            # Add headers to response
            response_headers = {
                "X-RateLimit-Limit": str(max_requests),
                "X-RateLimit-Reset": str(reset_time),
            }

            if not allowed:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Rate limit exceeded. Maximum {max_requests} requests per {window}.",
                    headers=response_headers,
                )

            # Execute the endpoint
            result = await func(*args, **kwargs)

            return result

        return wrapper

    return decorator
