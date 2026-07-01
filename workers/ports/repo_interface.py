from abc import ABC, abstractmethod
from shared.domain.entities.channel import ChannelEntity
from shared.domain.entities.country import CountryEntity
from shared.domain.entities.url_entity import URLEntity


class IRepo(ABC):
    """Interface for Repository."""

    @abstractmethod
    async def upsert_batch_channels(self, channels: list[ChannelEntity]) -> None:
        """Add new channels and update changed channels"""
        pass

    @abstractmethod
    async def upsert_batch_countries(self, countries: list[CountryEntity]) -> None:
        """Add new countries and update changed countries"""
        pass

    @abstractmethod
    async def upsert_batch_urls(self, urls: list[URLEntity]) -> None:
        """Add new URLs and update changed URLs"""
        pass
