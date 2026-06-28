import pytest
from unittest.mock import AsyncMock
from src.channel_app.application.search_country import SearchCountryService
from src.channel_app.domain.factories.country_factory import CountryFactory


async def test_search_country_success(mock_uow):
    filters = {"has_channels": True}
    search_return_value = [
        {
            "country_code": "US",
            "country_name": "United States of America",
            "capital": "Washington, D.C.",
            "timezone": "America/New_York",
            "channel_count": 8,
        },
        {
            "country_code": "US",
            "country_name": "United States of America",
            "capital": "Washington, D.C.",
            "timezone": "America/New_York",
            "channel_count": 8,
        },
    ]
    expected = [CountryFactory.create(**c) for c in search_return_value]
    mock_uow.countries.search.return_value = search_return_value

    service = SearchCountryService(mock_uow)
    result = await service.execute(filters)

    mock_uow.countries.search.assert_called_once_with(fields=[], filters=filters)
    assert result == expected


async def test_search_country_empty_result(mock_uow):
    mock_uow.countries.search.return_value = []

    service = SearchCountryService(mock_uow)
    result = await service.execute({})

    assert result == []
