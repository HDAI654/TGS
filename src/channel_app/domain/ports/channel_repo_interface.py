from abc import ABC, abstractmethod
from typing import Any
from src.channel_app.domain.entities.channel import ChannelEntity
from src.channel_app.domain.entities.url_entity import URLEntity
from src.core.id_vo import ID
from src.channel_app.domain.value_objects.country_code import CountryCode
from src.channel_app.domain.value_objects.name import Name
from src.channel_app.domain.value_objects.category import Category
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
        new_name: Name | None = None,
        new_category: Category | None = None,
        new_country_code: CountryCode | None = None,
        new_is_geo_blocked: IsGeoBlocked | None = None,
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
    async def search(
        self, fields: list[str], filters: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Search channels by filters and return specified fields."""
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
    async def add_new_url(self, channel_id: ID, url: URLEntity) -> None:
        """Add new url to a channel."""
        pass

    @abstractmethod
    async def remove_url(self, url_id: ID) -> None:
        """Remove a url from a channel."""
        pass

    @abstractmethod
    async def get_urls(self, channel_id: ID) -> list[URLEntity]:
        """Remove a url from a channel."""
        pass
