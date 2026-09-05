import logging
from typing import Tuple, Dict, Optional

from src.modules.channels.domain.entities.channel import Channel
from src.modules.channels.domain.ports.channel_repo_interface import ChannelRepository
from src.modules.channels.domain.exceptions import ChannelNotFoundError

logger = logging.getLogger(__name__)


class InMemoryChannelRepository(ChannelRepository):
    """
    In‑memory implementation of ChannelRepository for testing/development.
    Stores channels in a dict by ID.
    """

    def __init__(self, initial_data: Dict[str, Channel] = None) -> None:
        self._storage: Dict[str, Channel] = initial_data.copy() if initial_data else {}

    async def get_by_id(self, channel_id: str) -> Channel:
        logger.debug("InMemory: get_by_id(%s)", channel_id)
        channel = self._storage.get(channel_id)
        if channel is None:
            raise ChannelNotFoundError(f"Channel with id {channel_id} not found")
        return channel

    async def search(self, text: str, limit: int, offset: int) -> Tuple[Channel, ...]:
        logger.debug("InMemory: search(text='%s', limit=%d, offset=%d)", text, limit, offset)
        if not text:
            # If empty, return all paginated (or empty? Usually search with empty text returns all)
            all_items = list(self._storage.values())
        else:
            lower_text = text.lower()
            all_items = [
                ch for ch in self._storage.values()
                if (lower_text in ch.name.lower() or
                    lower_text in ch.category.lower() or
                    lower_text in ch.language.lower() or
                    lower_text in ch.country_code.lower())
            ]
        # Apply pagination
        paginated = all_items[offset:offset + limit]
        return tuple(paginated)

    async def exists_by_id(self, channel_id: str) -> bool:
        logger.debug("InMemory: exists_by_id(%s)", channel_id)
        return channel_id in self._storage

    # Helper methods for tests (not part of interface)
    def add(self, channel: Channel) -> None:
        """Add or update a channel in the repository."""
        self._storage[channel.id] = channel

    def clear(self) -> None:
        """Clear all data."""
        self._storage.clear()