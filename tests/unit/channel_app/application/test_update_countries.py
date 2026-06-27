import pytest
from unittest.mock import AsyncMock
from src.channel_app.application.update_countries_data import UpdateCountriesService


async def test_update_countries_success(mock_uow, mock_crawler):
    countries = [AsyncMock(), AsyncMock()]
    mock_crawler.extract_all_countries.return_value = countries

    service = UpdateCountriesService(mock_uow, mock_crawler)
    await service.execute()

    mock_crawler.extract_all_countries.assert_called_once()
    mock_uow.countries.upsert_batch.assert_called_once_with(countries)
    mock_uow.commit.assert_called_once()
