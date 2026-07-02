from abc import ABC, abstractmethod
from shared.domain.id_vo import ID
from shared.domain.entities.channel import ChannelEntity
from shared.domain.entities.country import CountryEntity
from shared.domain.entities.url_entity import URLEntity


class ICrawler(ABC):
    """Interface for Crawler."""

    @abstractmethod
    async def extract_all_countries(self) -> list[CountryEntity]:
        """Extract all countries."""
        pass

    @abstractmethod
    async def extract_all_channels(
        self,
    ) -> tuple[list[ChannelEntity], dict[ID, list[URLEntity]]]:
        """Extract all channels and their urls."""
        pass
