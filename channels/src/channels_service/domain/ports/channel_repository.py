from abc import ABC, abstractmethod
from uuid import UUID
from channels_service.domain.entities.channel import Channel


class ChannelRepository(ABC):
    @abstractmethod
    async def get_by_id(self, channel_id: UUID) -> Channel | None:
        raise NotImplementedError

    @abstractmethod
    async def get_all(self) -> list[Channel]:
        raise NotImplementedError

    @abstractmethod
    async def search(
        self, text: str, limit: int, offset: int
    ) -> tuple[list[Channel], int]:
        raise NotImplementedError

    @abstractmethod
    async def exist(self, id: UUID) -> bool:
        raise NotImplementedError
