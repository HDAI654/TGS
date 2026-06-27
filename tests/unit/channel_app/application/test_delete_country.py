import pytest
from src.channel_app.application.delete_country import DeleteCountryService
from src.core.exceptions import CountryNotFoundError


async def test_delete_country_success(mock_uow):
    country_code = "US"
    service = DeleteCountryService(mock_uow)
    await service.execute(country_code)

    mock_uow.countries.delete.assert_called_once()
    mock_uow.commit.assert_called_once()


async def test_delete_country_invalid_code(mock_uow):
    service = DeleteCountryService(mock_uow)
    with pytest.raises(CountryNotFoundError):
        await service.execute("invalid")
