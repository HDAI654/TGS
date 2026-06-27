import pytest
from src.channel_app.application.delete_channel import DeleteChannelService
from src.core.exceptions import ChannelNotFoundError


async def test_delete_channel_success(mock_uow):
    channel_id = "de565ed5exs3ss"
    service = DeleteChannelService(mock_uow)
    await service.execute(channel_id)

    mock_uow.channels.delete.assert_called_once()
    mock_uow.commit.assert_called_once()


async def test_delete_channel_invalid_id(mock_uow):
    service = DeleteChannelService(mock_uow)
    with pytest.raises(ChannelNotFoundError):
        await service.execute("bad-id")
