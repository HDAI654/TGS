from uuid import UUID
from src.domain.entities.channel import Channel
from src.domain.ports.channel_repository import ChannelRepository
from src.exceptions.application import InvalidPaginationError

_MIN_LIMIT = 1
_MAX_LIMIT = 100


def _validate_pagination(limit: int, offset: int) -> None:
    if not _MIN_LIMIT <= limit <= _MAX_LIMIT:
        raise InvalidPaginationError(
            f"limit must be between {_MIN_LIMIT} and {_MAX_LIMIT}"
        )
    if offset < 0:
        raise InvalidPaginationError("offset must be non-negative")


async def get_channel(
    repository: ChannelRepository, channel_id: UUID
) -> Channel | None:
    """Return a single channel by id, or None when not found."""
    return await repository.get_by_id(channel_id)


async def search_channels(
    repository: ChannelRepository,
    text: str | None,
    limit: int,
    offset: int,
) -> tuple[list[Channel], int] | None:
    """Search channels by free text.

    Returns None when text is missing or blank (no search requested).
    Otherwise returns (matching items, total count) with pagination applied.
    """
    _validate_pagination(limit, offset)
    if text is None or not text.strip():
        return None
    return await repository.search(text, limit, offset)
