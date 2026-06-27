import pytest
from src.channel_app.application.add_channel_url import AddChannelURLsService
from src.core.exceptions import ChannelNotFoundError


async def test_add_channel_url_success(mock_uow):
    channel_id = "4ef5ce2de45de2"
    url_link = "https://example.com"
    service = AddChannelURLsService(mock_uow)
    await service.execute(channel_id, url_link)

    mock_uow.channels.add_new_url.assert_called_once()
    mock_uow.commit.assert_called_once()


async def test_add_channel_url_invalid_id(mock_uow):
    service = AddChannelURLsService(mock_uow)
    with pytest.raises(ChannelNotFoundError):
        await service.execute("bad-id", "http://example.com")
