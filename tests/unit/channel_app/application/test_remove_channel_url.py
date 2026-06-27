import pytest
from src.channel_app.application.remove_channel_url import RemoveChannelURLsService
from src.core.exceptions import URLNotFoundError


async def test_remove_channel_url_success(mock_uow):
    url_id = "4ef5ce2de45de2"
    service = RemoveChannelURLsService(mock_uow)
    await service.execute(url_id)

    mock_uow.channels.remove_url.assert_called_once()
    mock_uow.commit.assert_called_once()


async def test_remove_channel_url_invalid_id(mock_uow):
    service = RemoveChannelURLsService(mock_uow)
    with pytest.raises(URLNotFoundError):
        await service.execute("bad-id")
