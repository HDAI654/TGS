from abc import ABC, abstractmethod
from workers.ports.repo_interface import IRepo


class IUnitOfWork(ABC):
    repo: IRepo

    @abstractmethod
    async def commit(self) -> None:
        pass

    @abstractmethod
    async def rollback(self) -> None:
        pass
