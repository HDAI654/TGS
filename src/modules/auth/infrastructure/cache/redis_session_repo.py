import logging
from src.modules.auth.domain.ports.session_repo_interface import ISessionRepository
from src.modules.auth.domain.entities.session import SessionEntity
from src.modules.auth.domain.value_objects.user_id import UserID
from src.modules.auth.domain.value_objects.session_id import SessionID
from src.modules.auth.domain.value_objects.date import Date
from src.modules.auth.domain.value_objects.device import Device
from src.modules.core.conf import Config
from src.modules.auth.exceptions import (
    SessionNotFoundError,
    CacheConnectionError,
    CacheTimeoutError,
    CacheOperationError,
)
from redis.asyncio import Redis
from redis.exceptions import RedisError, ConnectionError, TimeoutError

logger = logging.getLogger(__name__)


class RedisSessionRepository(ISessionRepository):
    SESSION_TTL_SECONDS = Config.REFRESH_TOKEN_EXPIRE_MINUTES * 60
    SESSION_KEY_PREFIX = Config.SESSION_KEY_PREFIX
    USER_SESSIONS_KEY_PREFIX = Config.USER_SESSIONS_KEY_PREFIX

    def __init__(self, client: Redis):
        self._client = client

    async def add(self, session: SessionEntity) -> None:
        logger.info(
            "Adding session: id=%s, user_id=%s", session.id.value, session.user_id.value
        )

        pipeline = self._client.pipeline()

        session_key = self._get_session_key(session.id)
        session_data = self._serialize_session(session)

        pipeline.hset(session_key, mapping=session_data)
        pipeline.expire(session_key, self.SESSION_TTL_SECONDS)

        user_sessions_key = self._get_user_sessions_key(session.user_id)
        pipeline.sadd(user_sessions_key, str(session.id.value))

        await self._execute_redis_operation(
            "add_session",
            pipeline.execute,
        )
        logger.info("Session added successfully: id=%s", session.id.value)

    async def extend_session(self, session_id: SessionID) -> None:
        logger.info("Extending session: id=%s", session_id.value)
        session_key = self._get_session_key(session_id)
        result = await self._execute_redis_operation(
            "extend_session",
            self._client.expire,
            session_key,
            self.SESSION_TTL_SECONDS,
        )

        if not result:
            raise SessionNotFoundError(
                f"Session with id {session_id.value!r} not found"
            )
        logger.info("Session extended successfully: id=%s", session_id.value)

    async def delete(self, session_id: SessionID, user_id: UserID) -> None:
        logger.info(
            "Deleting session: id=%s, user_id=%s", session_id.value, user_id.value
        )
        pipeline = self._client.pipeline()

        session_key = self._get_session_key(session_id)
        pipeline.delete(session_key)

        user_sessions_key = self._get_user_sessions_key(user_id)
        pipeline.srem(user_sessions_key, session_id.value)

        results = await self._execute_redis_operation(
            "delete_session",
            pipeline.execute,
        )

        if results[0] == 0:
            raise SessionNotFoundError(
                f"Session with id {session_id.value!r} not found"
            )
        logger.info("Session deleted successfully: id=%s", session_id.value)

    async def delete_all_other_sessions(
        self, current_session_id: SessionID, user_id: UserID
    ) -> None:
        logger.debug(
            "Deleting all sessions of user except current session: current_session_id=%s, user_id=%s",
            current_session_id.value,
            user_id.value,
        )
        user_sessions_key = self._get_user_sessions_key(user_id)
        all_session_ids = await self._client.smembers(user_sessions_key)

        sessions_to_delete = [
            sid for sid in all_session_ids if sid != current_session_id.value
        ]

        if not sessions_to_delete:
            return

        pipeline = self._client.pipeline()

        session_keys = [
            self._get_session_key(SessionID(sid)) for sid in sessions_to_delete
        ]
        pipeline.delete(*session_keys)

        pipeline.srem(user_sessions_key, *sessions_to_delete)
        await self._execute_redis_operation(
            "delete_all_other_sessions",
            pipeline.execute,
        )
        logger.debug(
            "Sessions deleted successfully: current_session_id=%s, user_id=%s",
            current_session_id.value,
            user_id.value,
        )

    async def get_by_id(self, session_id: SessionID) -> SessionEntity:
        logger.info("Start getting session: id=%s", session_id.value)
        session_key = self._get_session_key(session_id)
        session_data = await self._execute_redis_operation(
            "get_by_id",
            self._client.hgetall,
            session_key,
        )

        if not session_data:
            logger.debug("Session not found: id=%s", session_id.value)
            raise SessionNotFoundError(
                f"Session with id {session_id.value!r} not found"
            )
        logger.info("Session found: id=%s", session_id.value)
        return self._deserialize_session(session_data)

    async def get_by_user_id(self, user_id: UserID) -> list[SessionEntity]:
        logger.debug("Start getting user's sessions: user_id=%s", user_id.value)
        user_sessions_key = self._get_user_sessions_key(user_id)
        session_ids = await self._client.smembers(user_sessions_key)

        if not session_ids:
            logger.debug("No session found for this user: user_id=%s", user_id.value)
            return []

        pipeline = self._client.pipeline()
        for session_id in session_ids:
            session_key = self._get_session_key(SessionID(session_id))
            pipeline.hgetall(session_key)

        sessions_data = await self._execute_redis_operation(
            "get_by_user_id",
            pipeline.execute,
        )

        sessions = []
        for session_data in sessions_data:
            if session_data:
                session = self._deserialize_session(session_data)
                sessions.append(session)

        expired = [sid for sid, data in zip(session_ids, sessions_data) if not data]
        if expired:
            logger.debug(
                "Start deleting user's expired sessions: user_id=%s", user_id.value
            )
            await self._execute_redis_operation(
                "del_expired_sessions", self._client.srem, user_sessions_key, *expired
            )
            logger.debug(
                "User's expired sessions deleted successfully: user_id=%s",
                user_id.value,
            )

        return sessions

    def _get_session_key(self, session_id: SessionID) -> str:
        """Generate Redis key for a session"""
        return f"{self.SESSION_KEY_PREFIX}{session_id.value}"

    def _get_user_sessions_key(self, user_id: UserID) -> str:
        """Generate Redis key for user's sessions set"""
        return f"{self.USER_SESSIONS_KEY_PREFIX}{user_id.value}"

    def _deserialize_session(self, data: dict) -> SessionEntity:
        """Convert Redis hash data back to SessionEntity"""
        decoded_data = {
            key.decode() if isinstance(key, bytes) else key: (
                value.decode() if isinstance(value, bytes) else value
            )
            for key, value in data.items()
        }

        return SessionEntity(
            id=SessionID(decoded_data["id"]),
            user_id=UserID(decoded_data["user_id"]),
            device=Device(decoded_data["device"]),
            created_at=Date(decoded_data["created_at"]),
        )

    def _serialize_session(self, session: SessionEntity) -> dict:
        """Convert SessionEntity to Redis hash format"""
        return {
            "id": session.id.value,
            "user_id": session.user_id.value,
            "device": session.device.value,
            "created_at": session.created_at.value.isoformat(),
        }

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
