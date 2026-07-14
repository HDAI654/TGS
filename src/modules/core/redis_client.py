from src.modules.core.conf import Config
from redis.asyncio import Redis
from functools import lru_cache


@lru_cache(maxsize=1)
def get_redis_client() -> Redis:
    """Get async Redis client singleton"""
    if Config.APP_ENV == "development":
        import fakeredis

        return fakeredis.aioredis.FakeRedis(decode_responses=True)
    else:
        redis_url = Config.REDIS_URL
        return Redis.from_url(
            redis_url,
            decode_responses=True,  # Return strings instead of bytes
            max_connections=20,
            socket_timeout=5,
            socket_connect_timeout=5,
            retry_on_timeout=True,
        )


async def close_redis_client() -> None:
    """Close Redis connection (on shutdown)"""
    client = get_redis_client()
    await client.aclose()
