from abc import ABC, abstractmethod
from src.modules.channels.domain.value_objects.id import ID
from src.modules.channels.domain.entities.channel import ChannelEntity
from src.modules.channels.domain.entities.country import CountryEntity
from src.modules.channels.domain.entities.url_entity import URLEntity


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
