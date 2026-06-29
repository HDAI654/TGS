from abc import ABC, abstractmethod
from shared.domain.entities.channel import ChannelEntity
from shared.domain.entities.country import CountryEntity


class ICrawler(ABC):
    """Interface for Crawler."""

    @abstractmethod
    async def extract_all_countries(self) -> list[CountryEntity]:
        """Extract all countries."""
        pass

    @abstractmethod
    async def extract_all_channels(self) -> list[ChannelEntity]:
        """Extract all channels."""
        pass
