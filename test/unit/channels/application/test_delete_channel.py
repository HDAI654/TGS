import pytest
from src.modules.channels.domain.value_objects.id import ID
from src.modules.channels.application.delete_channel import DeleteChannelService
from src.modules.channels.exceptions import ChannelNotFoundError


async def test_delete_channel_success(mock_uow):
    channel_id = ID.generate().value
    mock_uow.channels.exists_by_id.return_value = True
    service = DeleteChannelService(mock_uow)
    await service.execute(channel_id)

    mock_uow.channels.delete.assert_called_once()
    mock_uow.commit.assert_called_once()


async def test_delete_channel_invalid_id(mock_uow):
    service = DeleteChannelService(mock_uow)
    with pytest.raises(ChannelNotFoundError):
        await service.execute("bad-id")
