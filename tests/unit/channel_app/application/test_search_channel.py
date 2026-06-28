import pytest
from unittest.mock import AsyncMock
from src.channel_app.application.search_channel import SearchChannelService
from src.channel_app.domain.factories.channel_factory import ChannelFactory


async def test_search_channel_success(mock_uow):
    filters = {"category": "news"}
    search_return_value = [
        {
            "id": "ewiubnewvce2ew",
            "name": "CNN",
            "category": "news",
            "language": "eng",
            "country_code": "US",
            "is_geo_blocked": False,
        },
        {
            "id": "ewibnewvcwe2ew",
            "name": "CNN",
            "category": "news",
            "language": "eng",
            "country_code": "US",
            "is_geo_blocked": False,
        },
    ]
    expected = [ChannelFactory.create(**ch) for ch in search_return_value]
    mock_uow.channels.search.return_value = search_return_value

    service = SearchChannelService(mock_uow)
    result = await service.execute(filters)

    mock_uow.channels.search.assert_called_once_with(fields=[], filters=filters)
    assert result == expected
