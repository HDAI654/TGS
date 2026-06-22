from abc import ABC, abstractmethod
from src.channel_app.domain.entities.channel import ChannelEntity
from src.core.id_vo import ID
from src.channel_app.domain.value_objects.name import Name
from src.channel_app.domain.value_objects.url import URL
from src.channel_app.domain.value_objects.language import Language
from src.channel_app.domain.value_objects.is_geo_blocked import IsGeoBlocked


class IChannelRepository(ABC):
    """Repository interface for Channel entities."""

    @abstractmethod
    async def add(self, channel: ChannelEntity) -> None:
        """Create a new channel in the database."""
        pass

    @abstractmethod
    async def update(
        self,
        channel_id: ID,
        name: Name = None,
        category: Name = None,
        stream_urls: list[URL] = None,
        youtube_urls: list[URL] = None,
        languages: list[Language] = None,
        country_id: ID = None,
        is_geo_blocked: IsGeoBlocked = None,
    ) -> None:
        """Update an existing channel in the database."""
        pass

    @abstractmethod
    async def add_new_url(self, channel_id: ID, url: URL, mode: str):
        """Add new url to a channel."""
        pass

    @abstractmethod
    async def delete(self, channel_id: ID) -> None:
        """Delete a channel by ID."""
        pass

    @abstractmethod
    async def get_by_id(self, channel_id: ID) -> ChannelEntity:
        """Get a channel by ID."""
        pass

    @abstractmethod
    async def get_channel_ids(self) -> list[ID]:
        """Get all IDs of channels"""
        pass

    @abstractmethod
    async def exists_by_id(self, channel_id: ID) -> bool:
        """Check if a channel exists by ID."""
        pass
