import pytest
from unittest.mock import AsyncMock
from src.modules.channels.domain.value_objects.id import ID
from src.modules.channels.application.get_channel import GetChannelService
from src.modules.channels.exceptions import ChannelNotFoundError


async def test_get_channel_success(mock_uow):
    channel_id = ID.generate().value
    mock_uow.channels.exists_by_id.return_value = True
    expected = AsyncMock()
    mock_uow.channels.get_by_id.return_value = expected

    service = GetChannelService(mock_uow)
    result = await service.execute(channel_id)

    mock_uow.channels.get_by_id.assert_called_once()
    assert result == expected


async def test_get_channel_invalid_id(mock_uow):
    service = GetChannelService(mock_uow)
    with pytest.raises(ChannelNotFoundError):
        await service.execute("bad-id")
