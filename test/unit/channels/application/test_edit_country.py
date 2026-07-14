import pytest
from src.modules.channels.application.edit_country import EditCountryService
from src.modules.channels.exceptions import CountryNotFoundError


async def test_edit_country_success(mock_uow):
    country_code = "US"
    new_name = "United States"
    new_capital = "Washington"
    new_timezone = "America/New_York"
    new_channel_count = 10

    service = EditCountryService(mock_uow)
    await service.execute(
        country_code, new_name, new_capital, new_timezone, new_channel_count
    )

    mock_uow.countries.update.assert_called_once()
    call_args = mock_uow.countries.update.call_args[1]
    assert call_args["country_code"].value == country_code
    assert call_args["new_country_name"].value == new_name
    assert call_args["new_capital"].value == new_capital
    assert call_args["new_timezone"].value == new_timezone
    assert call_args["new_channel_count"].value == new_channel_count
    mock_uow.commit.assert_called_once()


async def test_edit_country_invalid_code(mock_uow):
    service = EditCountryService(mock_uow)
    with pytest.raises(CountryNotFoundError):
        await service.execute("invalid")
