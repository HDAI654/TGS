import pytest
from unittest.mock import Mock
from src.modules.channels.domain.value_objects.id import ID
from src.modules.channels.application.remove_channel_url import RemoveChannelURLsService
from src.modules.channels.exceptions import URLNotFoundError


async def test_remove_channel_url_success(mock_uow):
    url_id = ID.generate().value
    mock_res = Mock()
    mock_res.rowcount = 1
    mock_uow.channels._execute_db_operation.return_value = mock_res
    service = RemoveChannelURLsService(mock_uow)
    await service.execute(url_id)

    mock_uow.channels.remove_url.assert_called_once()
    mock_uow.commit.assert_called_once()


async def test_remove_channel_url_invalid_id(mock_uow):
    service = RemoveChannelURLsService(mock_uow)
    with pytest.raises(URLNotFoundError):
        await service.execute("bad-id")
