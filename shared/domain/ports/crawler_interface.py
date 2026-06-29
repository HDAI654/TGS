from abc import ABC, abstractmethod
from shared.domain.entities.channel import ChannelEntity
from shared.domain.entities.country import CountryEntity
from shared.domain.value_objects.country_code import CountryCode


class ICrawler(ABC):
    """Interface for Crawler."""

    @abstractmethod
    async def extract_all_countries(self) -> list[CountryEntity]:
        """Extract all countries."""
        pass

    @abstractmethod
    async def extract_all_channels(
        self, country_codes: list[CountryCode]
    ) -> list[ChannelEntity]:
        """Extract all channels of all countries."""
        pass
