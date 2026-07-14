import pytest
from src.modules.channels.domain.value_objects.id import ID
from src.modules.channels.application.edit_channel import EditChannelService
from src.modules.channels.exceptions import ChannelNotFoundError


async def test_edit_channel_success(mock_uow):
    channel_id = ID.generate().value
    mock_uow.channels.exists_by_id.return_value = True
    new_name = "CNN"
    new_category = "News"
    new_country_code = "US"
    new_is_geo_blocked = True

    service = EditChannelService(mock_uow)
    await service.execute(
        channel_id, new_name, new_category, new_country_code, new_is_geo_blocked
    )

    mock_uow.channels.update.assert_called_once()
    call_args = mock_uow.channels.update.call_args[1]
    assert call_args["channel_id"].value == channel_id
    assert call_args["new_name"].value == new_name
    assert call_args["new_category"].value == new_category
    assert call_args["new_country_code"].value == new_country_code
    assert call_args["new_is_geo_blocked"].value == new_is_geo_blocked
    mock_uow.commit.assert_called_once()


async def test_edit_channel_invalid_id(mock_uow):
    service = EditChannelService(mock_uow)
    with pytest.raises(ChannelNotFoundError):
        await service.execute("bad-id")
