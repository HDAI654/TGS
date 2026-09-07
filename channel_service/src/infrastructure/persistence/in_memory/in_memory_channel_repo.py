"""In-memory implementation for channel repository interface."""

from uuid import UUID
from src.domain.entities.channel import Channel
from src.domain.ports.channel_repository import ChannelRepository


class InMemoryChannelRepository(ChannelRepository):
    """In-memory channel repository. Stores channels in a dict keyed by ID."""

    def __init__(
        self,
        channels: list[Channel] | None = None,
        country_name_map: dict[str, str] | None = None,
    ):
        self._channels: dict[UUID, Channel] = {c.id: c for c in (channels or [])}
        self._country_name_map: dict[str, str] = country_name_map or {}

    async def get_by_id(self, channel_id: UUID) -> Channel | None:
        return self._channels.get(channel_id)

    async def get_all(self) -> list[Channel]:
        return list(self._channels.values())

    async def search(
        self, text: str, limit: int, offset: int
    ) -> tuple[list[Channel], int]:
        pattern = text.lower()
        results = []
        for channel in self._channels.values():
            # Check all fields that the SQL version searches
            country_name = self._country_name_map.get(channel.country_code, "").lower()
            if (
                pattern in channel.name.lower()
                or pattern in channel.category.name.lower()
                or pattern in channel.language.lower()
                or pattern in channel.country_code.lower()
                or pattern in country_name
            ):
                results.append(channel)

        total = len(results)
        # Sort by name, then id to match SQL ordering
        results.sort(key=lambda c: (c.name.lower(), c.id))
        paginated = results[offset : offset + limit]
        return paginated, total

    async def exist(self, id: UUID) -> bool:
        return id in self._channels
