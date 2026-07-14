from abc import ABC, abstractmethod
from src.modules.auth.domain.entities.session import SessionEntity
from src.modules.auth.domain.value_objects.user_id import UserID
from src.modules.auth.domain.value_objects.session_id import SessionID


class ISessionRepository(ABC):
    """Repository interface for Session entities."""

    SESSION_TTL_SECONDS: int
    SESSION_KEY_PREFIX: str
    USER_SESSIONS_KEY_PREFIX: str

    @abstractmethod
    async def add(self, session: SessionEntity) -> None:
        """
        Create a new session in the database.

        Raises:
            CacheConnectionError: Raised when cannot connect to cache.
            CacheTimeoutError: Raised when cache operation times out.
            CacheOperationError: Raised when cache operation fails.
        """
        pass

    @abstractmethod
    async def extend_session(self, session_id: SessionID) -> None:
        """
        Extend the session's expiration time.

        Raises:
            CacheConnectionError: Raised when cannot connect to cache.
            CacheTimeoutError: Raised when cache operation times out.
            CacheOperationError: Raised when cache operation fails.
            SessionNotFoundError: Raised when Session not found.
        """
        pass

    @abstractmethod
    async def delete(self, session_id: SessionID, user_id: UserID) -> None:
        """
        Delete a single session by SessionID.

        Raises:
            CacheConnectionError: Raised when cannot connect to cache.
            CacheTimeoutError: Raised when cache operation times out.
            CacheOperationError: Raised when cache operation fails.
            SessionNotFoundError: Raised when Session not found.
        """
        pass

    @abstractmethod
    async def delete_all_other_sessions(
        self, current_session_id: SessionID, user_id: UserID
    ) -> None:
        """
        Delete all sessions for a user except the current one.

        Raises:
            CacheConnectionError: Raised when cannot connect to cache.
            CacheTimeoutError: Raised when cache operation times out.
            CacheOperationError: Raised when cache operation fails.
        """
        pass

    @abstractmethod
    async def get_by_id(self, session_id: SessionID) -> SessionEntity:
        """
        Get a session by SessionID.

        Raises:
            CacheConnectionError: Raised when cannot connect to cache.
            CacheTimeoutError: Raised when cache operation times out.
            CacheOperationError: Raised when cache operation fails.
            SessionNotFoundError: Raised when Session not found.
        """
        pass

    @abstractmethod
    async def get_by_user_id(self, user_id: UserID) -> list[SessionEntity]:
        """
        Get a session by UserID.

        Raises:
            CacheConnectionError: Raised when cannot connect to cache.
            CacheTimeoutError: Raised when cache operation times out.
            CacheOperationError: Raised when cache operation fails.
        """
        pass
