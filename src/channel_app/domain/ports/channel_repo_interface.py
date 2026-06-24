from abc import ABC, abstractmethod
from src.channel_app.domain.entities.channel import ChannelEntity
from src.core.id_vo import ID
from src.channel_app.domain.value_objects.country_code import CountryCode
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
        country_id: ID = None,
        is_geo_blocked: IsGeoBlocked = None,
    ) -> None:
        """Update an existing channel in the database."""
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
    async def get_full_by_id(self, channel_id: ID) -> ChannelEntity:
        """Get a full data of a channel (its data + urls + languages) by ID."""
        pass

    @abstractmethod
    async def get_by_country_code(
        self, country_code: CountryCode
    ) -> list[ChannelEntity]:
        """Get all channels of a country"""
        pass

    @abstractmethod
    async def exists_by_id(self, channel_id: ID) -> bool:
        """Check if a channel exists by ID."""
        pass

    @abstractmethod
    async def upsert_batch(self, channels: list[ChannelEntity]) -> None:
        """Add new channels and update changed channels"""
        pass

    @abstractmethod
    async def add_new_url(self, channel_id: ID, url: URL, mode: str):
        """Add new url to a channel."""
        pass

    @abstractmethod
    async def remove_url(self, channel_id: ID, url: URL):
        """Remove a url from a channel."""
        pass

    @abstractmethod
    async def add_new_language(self, channel_id: ID, language: Language):
        """Add new language to a channel."""
        pass

    @abstractmethod
    async def remove_language(self, channel_id: ID, language: Language):
        """Remove a language from a channel."""
        pass
