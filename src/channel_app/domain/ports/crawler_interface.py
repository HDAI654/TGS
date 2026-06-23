from abc import ABC, abstractmethod
from src.channel_app.domain.entities.channel import ChannelEntity
from src.channel_app.domain.entities.country import CountryEntity
from src.channel_app.domain.value_objects.country_code import CountryCode


class ICrawler(ABC):
    """Interface for Crawler."""

    @abstractmethod
    async def extract_all_countries(self) -> list[CountryEntity]:
        """Extract all countries."""
        pass

    @abstractmethod
    async def extract_all_channels(self) -> list[ChannelEntity]:
        """Extract all channels of all countries."""
        pass
