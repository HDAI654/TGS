import pytest
from unittest.mock import AsyncMock
from src.modules.channels.domain.value_objects.id import ID
from src.modules.channels.application.get_channel_urls import GetChannelURLsService
from src.modules.channels.exceptions import ChannelNotFoundError


async def test_get_channel_urls_success(mock_uow):
    channel_id = ID.generate().value
    mock_uow.channels.exists_by_id.return_value = True
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
