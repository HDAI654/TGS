import pytest
from unittest.mock import AsyncMock
from src.channel_app.application.update_channels_data import UpdateChannelsService


async def test_update_channels_success(mock_uow, mock_crawler):
    country_codes = ["US", "CA"]
    channels = [AsyncMock(), AsyncMock()]
    mock_uow.countries.get_country_codes.return_value = country_codes
    mock_crawler.extract_all_channels.return_value = channels

    service = UpdateChannelsService(mock_uow, mock_crawler)
    await service.execute()

    mock_uow.countries.get_country_codes.assert_called_once()
    mock_crawler.extract_all_channels.assert_called_once_with(country_codes)
    mock_uow.channels.upsert_batch.assert_called_once_with(channels)
    mock_uow.commit.assert_called_once()
