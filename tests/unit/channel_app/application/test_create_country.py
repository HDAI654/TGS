import pytest
from src.channel_app.application.create_country import CreateCountryService


async def test_create_country_success(mock_uow):
    country_data = {
        "country_code": "US",
        "country_name": "United States",
        "capital": "Washington",
        "timezone": "America/New_York",
        "channel_count": 10,
    }
    mock_uow.countries.add.return_value = None

    service = CreateCountryService(mock_uow)
    result = await service.execute(**country_data)

    mock_uow.countries.add.assert_called_once()
    mock_uow.commit.assert_called_once()
    assert result is not None
