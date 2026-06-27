import pytest
from unittest.mock import AsyncMock
from src.channel_app.application.get_channel import GetChannelService
from src.core.exceptions import ChannelNotFoundError


async def test_get_channel_success(mock_uow):
    channel_id = "e54e5d0wecjs58"
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
