import logging
import os
import secrets

import redis
from celery.exceptions import Ignore
from redis.exceptions import RedisError

from tgs_admin.celery import app

logger = logging.getLogger(__name__)

LOCK_KEY = "tgs:worker:update_data:lock"
TASK_TIME_LIMIT_SECONDS = int(os.getenv("UPDATE_DATA_TIME_LIMIT_SECONDS", "300"))
_configured_lock_ttl = int(os.getenv("UPDATE_DATA_LOCK_TTL_SECONDS", "600"))
LOCK_TTL_SECONDS = max(_configured_lock_ttl, TASK_TIME_LIMIT_SECONDS + 60)
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")


class UpdateDataLock:
    """Distributed Redis lock preventing overlapping update executions."""

    def __init__(self) -> None:
        self._client = redis.Redis.from_url(REDIS_URL, decode_responses=True)
        self._token = secrets.token_urlsafe(32)

    def acquire(self) -> bool:
        """Acquire the update-data lock if no execution is currently active."""
        return bool(
            self._client.set(
                LOCK_KEY,
                self._token,
                nx=True,
                ex=LOCK_TTL_SECONDS,
            )
        )

    def close(self) -> None:
        """Close the Redis client used by this lock."""
        self._client.close()

    def release(self) -> None:
        """Release this lock only when it is still owned by this execution."""
        script = """
        if redis.call('get', KEYS[1]) == ARGV[1] then
            return redis.call('del', KEYS[1])
        end
        return 0
        """
        try:
            self._client.eval(script, 1, LOCK_KEY, self._token)
        finally:
            self.close()


@app.task(
    bind=True,
    name="tgs_admin.apps.worker_control.tasks.update_data",
    time_limit=TASK_TIME_LIMIT_SECONDS,
    soft_time_limit=max(1, TASK_TIME_LIMIT_SECONDS - 30),
    acks_late=True,
    reject_on_worker_lost=True,
)
def update_data(self) -> None:
    """Run the periodic data update placeholder without overlapping executions."""
    lock = UpdateDataLock()
    try:
        acquired = lock.acquire()
    except RedisError:
        lock.close()
        raise

    if not acquired:
        logger.warning("update_data skipped because another execution is active")
        lock.close()
        raise Ignore()

    try:
        logger.info("update_data started")
        # Future channel/country synchronization logic belongs here.
        logger.info("update_data finished")
    finally:
        lock.release()
