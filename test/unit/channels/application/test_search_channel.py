import pytest
from unittest.mock import AsyncMock
from src.modules.channels.application.search_channel import SearchChannelService


async def test_search_channel_success(mock_uow):
    filters = {"category": "news"}
    expected = [AsyncMock(), AsyncMock()]
    mock_uow.channels.search.return_value = expected

    service = SearchChannelService(mock_uow)
    result = await service.execute(filters)

    mock_uow.channels.search.assert_called_once_with(filters=filters)
    assert result == expected
