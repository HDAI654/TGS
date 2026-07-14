from abc import ABC, abstractmethod
from src.modules.channels.domain.ports.country_repo_interface import ICountryRepository
from src.modules.channels.domain.ports.channel_repo_interface import IChannelRepository


class IUnitOfWork(ABC):
    countries: ICountryRepository
    channels: IChannelRepository

    @abstractmethod
    async def commit(self) -> None:
        pass

    @abstractmethod
    async def rollback(self) -> None:
        pass
