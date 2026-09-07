import pytest
from src.exceptions.application import InvalidPaginationError
from src.application.queries import search_countries


@pytest.mark.asyncio
async def test_search_countries_valid(mock_country_repo, sample_country):
    text = "united"
    limit = 5
    offset = 0
    expected = ([sample_country], 1)
    mock_country_repo.search_return = expected

    result = await search_countries(mock_country_repo, text, limit, offset)

    assert result == expected
    assert mock_country_repo.search_called_with == (text, limit, offset)


@pytest.mark.asyncio
async def test_search_countries_text_none(mock_country_repo):
    result = await search_countries(mock_country_repo, None, 10, 0)

    assert result is None
    assert mock_country_repo.search_called_with is None


@pytest.mark.asyncio
async def test_search_countries_text_empty(mock_country_repo):
    result = await search_countries(mock_country_repo, "", 10, 0)

    assert result is None
    assert mock_country_repo.search_called_with is None


@pytest.mark.asyncio
async def test_search_countries_text_whitespace(mock_country_repo):
    result = await search_countries(mock_country_repo, "   ", 10, 0)

    assert result is None
    assert mock_country_repo.search_called_with is None


@pytest.mark.asyncio
async def test_search_countries_limit_too_low(mock_country_repo):
    with pytest.raises(InvalidPaginationError) as excinfo:
        await search_countries(mock_country_repo, "test", 0, 0)
    assert "limit must be between" in str(excinfo.value)


@pytest.mark.asyncio
async def test_search_countries_limit_too_high(mock_country_repo):
    with pytest.raises(InvalidPaginationError):
        await search_countries(mock_country_repo, "test", 101, 0)


@pytest.mark.asyncio
async def test_search_countries_offset_negative(mock_country_repo):
    with pytest.raises(InvalidPaginationError) as excinfo:
        await search_countries(mock_country_repo, "test", 10, -1)
    assert "offset must be non-negative" in str(excinfo.value)


@pytest.mark.asyncio
async def test_search_countries_repository_raises(mock_country_repo):
    async def raise_exception(*args, **kwargs):
        raise RuntimeError("Search error")

    mock_country_repo.search = raise_exception

    with pytest.raises(RuntimeError, match="Search error"):
        await search_countries(mock_country_repo, "test", 10, 0)