import pytest
from unittest.mock import AsyncMock
from src.channel_app.application.get_channel_urls import GetChannelURLsService
from src.core.exceptions import ChannelNotFoundError


async def test_get_channel_urls_success(mock_uow):
    channel_id = "4ef5ce2de45de2"
    expected_urls = [AsyncMock(), AsyncMock()]
    mock_uow.channels.get_urls.return_value = expected_urls

    service = GetChannelURLsService(mock_uow)
    result = await service.execute(channel_id)

    mock_uow.channels.get_urls.assert_called_once()
    assert result == expected_urls


async def test_get_channel_urls_invalid_id(mock_uow):
    service = GetChannelURLsService(mock_uow)
    with pytest.raises(ChannelNotFoundError):
        await service.execute("bad-id")
