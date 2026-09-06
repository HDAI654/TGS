import pytest
from src.application.queries.channel_queries import search_channels
from src.application.queries.country_queries import search_countries


class Repository:
    async def search(self, text, limit, offset):
        return [text, limit, offset], 1


@pytest.mark.asyncio
@pytest.mark.parametrize("value", [None, "", " ", "   ", "\t"])
async def test_empty_channel_search_returns_none(value):
    assert await search_channels(Repository(), value, 10, 0) is None


@pytest.mark.asyncio
async def test_channel_search_delegates_non_empty_text():
    assert await search_channels(Repository(), "News", 10, 2) == (["News", 10, 2], 1)


@pytest.mark.asyncio
@pytest.mark.parametrize("value", [None, "", " ", "   ", "\t"])
async def test_empty_country_search_returns_none(value):
    assert await search_countries(Repository(), value, 10, 0) is None


@pytest.mark.asyncio
async def test_country_search_delegates_non_empty_text():
    assert await search_countries(Repository(), "Iran", 10, 2) == (["Iran", 10, 2], 1)



@pytest.mark.asyncio
async def test_channel_search_preserves_literal_wildcards() -> None:
    from src.infrastructure.persistence.repositories import _search_pattern

    assert _search_pattern("50%_\\") == "%50\\%\\_\\\\%"
