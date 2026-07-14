import pytest
from unittest.mock import AsyncMock
from src.modules.channels.application.get_country import GetCountryService
from src.modules.channels.exceptions import CountryNotFoundError


async def test_get_country_success(mock_uow):
    code = "US"
    expected = AsyncMock()
    mock_uow.countries.get_by_code.return_value = expected

    service = GetCountryService(mock_uow)
    result = await service.execute(code)

    mock_uow.countries.get_by_code.assert_called_once()
    assert result == expected


async def test_get_country_invalid_code(mock_uow):
    service = GetCountryService(mock_uow)
    with pytest.raises(CountryNotFoundError):
        await service.execute("invalid")


async def test_get_country_not_found(mock_uow):
    mock_uow.countries.get_by_code.side_effect = CountryNotFoundError

    service = GetCountryService(mock_uow)
    with pytest.raises(CountryNotFoundError):
        await service.execute("US")
