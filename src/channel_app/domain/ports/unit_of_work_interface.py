from abc import ABC, abstractmethod
from src.channel_app.domain.ports.country_repo_interface import ICountryRepository
from src.channel_app.domain.ports.channel_repo_interface import IChannelRepository


class IUnitOfWork(ABC):
    country: ICountryRepository
    channel: IChannelRepository

    @abstractmethod
    async def commit(self) -> None:
        pass

    @abstractmethod
    async def rollback(self) -> None:
        pass
