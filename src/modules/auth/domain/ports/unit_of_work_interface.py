from abc import ABC, abstractmethod
from src.modules.auth.domain.ports.user_repo_interface import (
    IUserRepository,
)


class IUnitOfWork(ABC):

    users: IUserRepository

    @abstractmethod
    async def commit(self) -> None:
        pass

    @abstractmethod
    async def rollback(self) -> None:
        pass
