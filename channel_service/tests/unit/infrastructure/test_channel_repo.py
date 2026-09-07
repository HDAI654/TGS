"""Tests for SQLAlchemyChannelRepository."""

from unittest.mock import AsyncMock, MagicMock, call

import pytest
from sqlalchemy.exc import DBAPIError, OperationalError, TimeoutError as SATimeoutError

from src.domain.entities.channel import Channel
from src.exceptions.infrastructure import (
    DatabaseConnectionError,
    DatabaseOperationError,
    DatabaseTimeoutError,
)
from src.infrastructure.persistence.repositories import SQLAlchemyChannelRepository


@pytest.mark.asyncio
async def test_get_by_id_found(mock_session, sample_channel_model):
    """Test get_by_id returns a Channel when found."""
    mock_result = AsyncMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=sample_channel_model)
    mock_session.execute = AsyncMock(return_value=mock_result)

    repo = SQLAlchemyChannelRepository(mock_session)
    channel_id = "12345678-1234-1234-1234-123456789abc"

    result = await repo.get_by_id(channel_id)

    assert isinstance(result, Channel)
    assert result.id == sample_channel_model.id
    assert result.name == sample_channel_model.name
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_by_id_not_found(mock_session):
    """Test get_by_id returns None when no channel found."""
    mock_result = AsyncMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=None)
    mock_session.execute = AsyncMock(return_value=mock_result)

    repo = SQLAlchemyChannelRepository(mock_session)
    result = await repo.get_by_id("some-id")

    assert result is None
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_by_id_timeout(mock_session):
    """Test get_by_id raises DatabaseTimeoutError on timeout."""
    mock_session.execute = AsyncMock(side_effect=SATimeoutError("timeout"))
    repo = SQLAlchemyChannelRepository(mock_session)

    with pytest.raises(DatabaseTimeoutError):
        await repo.get_by_id("some-id")


@pytest.mark.asyncio
async def test_get_by_id_connection_error(mock_session):
    """Test get_by_id raises DatabaseConnectionError on OperationalError."""
    mock_session.execute = AsyncMock(side_effect=OperationalError("error", {}, None))
    repo = SQLAlchemyChannelRepository(mock_session)

    with pytest.raises(DatabaseConnectionError):
        await repo.get_by_id("some-id")


@pytest.mark.asyncio
async def test_get_by_id_dbapi_error(mock_session):
    """Test get_by_id raises DatabaseOperationError on DBAPIError."""
    mock_session.execute = AsyncMock(side_effect=DBAPIError("dbapi error", None, None))
    repo = SQLAlchemyChannelRepository(mock_session)

    with pytest.raises(DatabaseOperationError):
        await repo.get_by_id("some-id")


@pytest.mark.asyncio
async def test_get_all(mock_session, sample_channel_model):
    """Test get_all returns list of Channels."""
    mock_result = AsyncMock()
    mock_scalars = MagicMock()
    mock_scalars.all = MagicMock(return_value=[sample_channel_model])
    mock_result.scalars = MagicMock(return_value=mock_scalars)
    mock_session.execute = AsyncMock(return_value=mock_result)

    repo = SQLAlchemyChannelRepository(mock_session)
    results = await repo.get_all()

    assert len(results) == 1
    assert isinstance(results[0], Channel)
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_search(mock_session, sample_channel_model):
    """Test search returns channels and total count."""
    # Count result
    count_result = AsyncMock()
    count_result.scalar_one = MagicMock(return_value=1)

    # Channel result
    channel_result = AsyncMock()
    scalars_mock = MagicMock()
    scalars_mock.all = MagicMock(return_value=[sample_channel_model])
    channel_result.scalars = MagicMock(return_value=scalars_mock)

    # Execute side effect: first call for count, second for channels
    mock_session.execute = AsyncMock(side_effect=[count_result, channel_result])

    repo = SQLAlchemyChannelRepository(mock_session)
    channels, total = await repo.search("news", limit=10, offset=0)

    assert len(channels) == 1
    assert total == 1
    assert mock_session.execute.await_count == 2


@pytest.mark.asyncio
async def test_search_error(mock_session):
    """Test search raises DatabaseOperationError on DB error."""
    mock_session.execute = AsyncMock(side_effect=OperationalError("error", {}, None))
    repo = SQLAlchemyChannelRepository(mock_session)

    with pytest.raises(DatabaseConnectionError):
        await repo.search("news", 10, 0)


@pytest.mark.asyncio
async def test_exist_true(mock_session):
    """Test exist returns True if channel exists."""
    mock_result = AsyncMock()
    mock_result.scalar_one_or_none = MagicMock(return_value="some-id")
    mock_session.execute = AsyncMock(return_value=mock_result)

    repo = SQLAlchemyChannelRepository(mock_session)
    exists = await repo.exist("some-id")

    assert exists is True
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_exist_false(mock_session):
    """Test exist returns False if channel does not exist."""
    mock_result = AsyncMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=None)
    mock_session.execute = AsyncMock(return_value=mock_result)

    repo = SQLAlchemyChannelRepository(mock_session)
    exists = await repo.exist("some-id")

    assert exists is False


@pytest.mark.asyncio
async def test_exist_error(mock_session):
    """Test exist raises DatabaseTimeoutError on timeout."""
    mock_session.execute = AsyncMock(side_effect=SATimeoutError("timeout"))
    repo = SQLAlchemyChannelRepository(mock_session)

    with pytest.raises(DatabaseTimeoutError):
        await repo.exist("some-id")