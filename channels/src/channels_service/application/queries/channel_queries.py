from uuid import UUID
from channels_service.domain.entities.channel import Channel
from channels_service.domain.ports.channel_repository import ChannelRepository


async def get_channel(repository: ChannelRepository, channel_id: UUID) -> Channel | None:
    return await repository.get_by_id(channel_id)


async def search_channels(
    repository: ChannelRepository,
    text: str | None,
    limit: int,
    offset: int,
) -> tuple[list[Channel], int] | None:
    if text is None or not text.strip():
        return None
    return await repository.search(text, limit, offset)
