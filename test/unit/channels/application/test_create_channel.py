import pytest
from src.modules.channels.application.create_channel import CreateChannelService


async def test_create_channel_success(mock_uow):
    channel_data = {
        "name": "CNN",
        "category": "news",
        "language": "eng",
        "country_code": "US",
        "is_geo_blocked": False,
    }
    service = CreateChannelService(mock_uow)
    result = await service.execute(**channel_data)

    mock_uow.channels.add.assert_called_once()
    mock_uow.commit.assert_called_once()
    assert result is not None
