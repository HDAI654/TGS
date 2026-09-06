from abc import ABC, abstractmethod
from channels_service.domain.entities.country import Country


class CountryRepository(ABC):
    @abstractmethod
    async def get_by_id(self, country_code: str) -> Country | None:
        raise NotImplementedError

    @abstractmethod
    async def get_all(self) -> list[Country]:
        raise NotImplementedError

    @abstractmethod
    async def search(self, text: str, limit: int, offset: int) -> tuple[list[Country], int]:
        raise NotImplementedError

    @abstractmethod
    async def exist(self, id: str) -> bool:
        raise NotImplementedError
