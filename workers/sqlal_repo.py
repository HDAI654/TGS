from workers.repo_interface import IRepo
from shared.domain.entities.channel import ChannelEntity
from shared.domain.entities.country import CountryEntity
from shared.domain.entities.url_entity import URLEntity


class SQLAL_Repo(IRepo):
    """SQLAlchemy implemantation for channel, country and URL entities."""

    async def upsert_batch_channels(self, channels: list[ChannelEntity]) -> None:
        pass

    async def upsert_batch_countries(self, countries: list[CountryEntity]) -> None:
        pass

    async def upsert_batch_urls(self, urls: list[URLEntity]) -> None:
        pass
