import pytest
from unittest.mock import AsyncMock
from src.modules.channels.application.search_country import SearchCountryService


async def test_search_country_success(mock_uow):
    filters = {"has_channels": True}
    expected = [AsyncMock(), AsyncMock()]
    mock_uow.countries.search.return_value = expected

    service = SearchCountryService(mock_uow)
    result = await service.execute(filters)

    mock_uow.countries.search.assert_called_once_with(filters=filters)
    assert result == expected


async def test_search_country_empty_result(mock_uow):
    mock_uow.countries.search.return_value = []

    service = SearchCountryService(mock_uow)
    result = await service.execute({})

    assert result == []
