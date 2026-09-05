from abc import ABC, abstractmethod
from src.modules.channels.domain.entities.channel import Channel

class ChannelRepository(ABC):
    """Repository interface for Channel entities."""

    @abstractmethod
    async def get_by_id(self, channel_id: str) -> Channel:
        """Get a channel by ID.

        Raises:
            DatabaseConnectionError: Raised when cannot connect to database.
            DatabaseTimeoutError: Raised when database operation times out.
            DatabaseOperationError: Raised when database operation fails.
            ChannelNotFoundError: Raised when Channel not found.
        """
        pass

    @abstractmethod
    async def search(self, text: str, limit: int, offset: int) -> tuple[Channel, ...]:
        """Search channels.

        Raises:
            DatabaseConnectionError: Raised when cannot connect to database.
            DatabaseTimeoutError: Raised when database operation times out.
            DatabaseOperationError: Raised when database operation fails.
        """
        pass

    @abstractmethod
    async def exists_by_id(self, channel_id: str) -> bool:
        """Check if a channel exists by ID.

        Raises:
            DatabaseConnectionError: Raised when cannot connect to database.
            DatabaseTimeoutError: Raised when database operation times out.
            DatabaseOperationError: Raised when database operation fails.
        """
        pass