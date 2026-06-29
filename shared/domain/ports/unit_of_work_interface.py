from abc import ABC, abstractmethod
from shared.domain.ports.country_repo_interface import ICountryRepository
from shared.domain.ports.channel_repo_interface import IChannelRepository


class IUnitOfWork(ABC):
    countries: ICountryRepository
    channels: IChannelRepository

    @abstractmethod
    async def commit(self) -> None:
        pass

    @abstractmethod
    async def rollback(self) -> None:
        pass
