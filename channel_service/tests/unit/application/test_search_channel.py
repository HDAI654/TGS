import pytest
from src.exceptions.application import InvalidPaginationError
from src.application.queries import search_channels


@pytest.mark.asyncio
async def test_search_channels_valid(mock_channel_repo, sample_channel):
    text = "test"
    limit = 10
    offset = 0
    expected = ([sample_channel], 1)
    mock_channel_repo.search_return = expected

    result = await search_channels(mock_channel_repo, text, limit, offset)

    assert result == expected
    assert mock_channel_repo.search_called_with == (text, limit, offset)


@pytest.mark.asyncio
async def test_search_channels_text_none(mock_channel_repo):
    result = await search_channels(mock_channel_repo, None, 10, 0)

    assert result is None
    assert mock_channel_repo.search_called_with is None


@pytest.mark.asyncio
async def test_search_channels_text_empty(mock_channel_repo):
    result = await search_channels(mock_channel_repo, "", 10, 0)

    assert result is None
    assert mock_channel_repo.search_called_with is None


@pytest.mark.asyncio
async def test_search_channels_text_whitespace(mock_channel_repo):
    result = await search_channels(mock_channel_repo, "   ", 10, 0)

    assert result is None
    assert mock_channel_repo.search_called_with is None


@pytest.mark.asyncio
async def test_search_channels_limit_too_low(mock_channel_repo):
    with pytest.raises(InvalidPaginationError) as excinfo:
        await search_channels(mock_channel_repo, "test", 0, 0)
    assert "limit must be between" in str(excinfo.value)


@pytest.mark.asyncio
async def test_search_channels_limit_too_high(mock_channel_repo):
    with pytest.raises(InvalidPaginationError):
        await search_channels(mock_channel_repo, "test", 101, 0)


@pytest.mark.asyncio
async def test_search_channels_offset_negative(mock_channel_repo):
    with pytest.raises(InvalidPaginationError) as excinfo:
        await search_channels(mock_channel_repo, "test", 10, -1)
    assert "offset must be non-negative" in str(excinfo.value)


@pytest.mark.asyncio
async def test_search_channels_repository_raises(mock_channel_repo):
    async def raise_exception(*args, **kwargs):
        raise RuntimeError("Search error")

    mock_channel_repo.search = raise_exception

    with pytest.raises(RuntimeError, match="Search error"):
        await search_channels(mock_channel_repo, "test", 10, 0)