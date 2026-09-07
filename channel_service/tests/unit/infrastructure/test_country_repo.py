"""Tests for SQLAlchemyCountryRepository."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.exc import DBAPIError, OperationalError, TimeoutError as SATimeoutError

from src.domain.entities.country import Country
from src.exceptions.infrastructure import (
    DatabaseConnectionError,
    DatabaseOperationError,
    DatabaseTimeoutError,
)
from src.infrastructure.persistence.repositories import SQLAlchemyCountryRepository


@pytest.mark.asyncio
async def test_get_by_id_found(mock_session, sample_country_model):
    """Test get_by_id returns a Country when found."""
    mock_result = AsyncMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=sample_country_model)
    mock_session.execute = AsyncMock(return_value=mock_result)

    repo = SQLAlchemyCountryRepository(mock_session)
    result = await repo.get_by_id("US")

    assert isinstance(result, Country)
    assert result.country_code == "US"
    assert result.country_name == "United States"
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_by_id_not_found(mock_session):
    """Test get_by_id returns None when no country found."""
    mock_result = AsyncMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=None)
    mock_session.execute = AsyncMock(return_value=mock_result)

    repo = SQLAlchemyCountryRepository(mock_session)
    result = await repo.get_by_id("XX")

    assert result is None


@pytest.mark.asyncio
async def test_get_by_id_timeout(mock_session):
    """Test get_by_id raises DatabaseTimeoutError on timeout."""
    mock_session.execute = AsyncMock(side_effect=SATimeoutError("timeout"))
    repo = SQLAlchemyCountryRepository(mock_session)

    with pytest.raises(DatabaseTimeoutError):
        await repo.get_by_id("US")


@pytest.mark.asyncio
async def test_get_by_id_connection_error(mock_session):
    """Test get_by_id raises DatabaseConnectionError on OperationalError."""
    mock_session.execute = AsyncMock(side_effect=OperationalError("error", {}, None))
    repo = SQLAlchemyCountryRepository(mock_session)

    with pytest.raises(DatabaseConnectionError):
        await repo.get_by_id("US")


@pytest.mark.asyncio
async def test_get_by_id_dbapi_error(mock_session):
    """Test get_by_id raises DatabaseOperationError on DBAPIError."""
    mock_session.execute = AsyncMock(side_effect=DBAPIError("dbapi error", None, None))
    repo = SQLAlchemyCountryRepository(mock_session)

    with pytest.raises(DatabaseOperationError):
        await repo.get_by_id("US")


@pytest.mark.asyncio
async def test_get_all(mock_session, sample_country_model):
    """Test get_all returns list of Countries."""
    mock_result = AsyncMock()
    mock_scalars = MagicMock()
    mock_scalars.all = MagicMock(return_value=[sample_country_model])
    mock_result.scalars = MagicMock(return_value=mock_scalars)
    mock_session.execute = AsyncMock(return_value=mock_result)

    repo = SQLAlchemyCountryRepository(mock_session)
    results = await repo.get_all()

    assert len(results) == 1
    assert isinstance(results[0], Country)
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_search(mock_session, sample_country_model):
    """Test search returns countries and total count."""
    count_result = AsyncMock()
    count_result.scalar_one = MagicMock(return_value=1)

    country_result = AsyncMock()
    scalars_mock = MagicMock()
    scalars_mock.all = MagicMock(return_value=[sample_country_model])
    country_result.scalars = MagicMock(return_value=scalars_mock)

    mock_session.execute = AsyncMock(side_effect=[count_result, country_result])

    repo = SQLAlchemyCountryRepository(mock_session)
    countries, total = await repo.search("united", limit=10, offset=0)

    assert len(countries) == 1
    assert total == 1
    assert mock_session.execute.await_count == 2


@pytest.mark.asyncio
async def test_search_error(mock_session):
    """Test search raises DatabaseOperationError on DB error."""
    mock_session.execute = AsyncMock(side_effect=OperationalError("error", {}, None))
    repo = SQLAlchemyCountryRepository(mock_session)

    with pytest.raises(DatabaseConnectionError):
        await repo.search("united", 10, 0)


@pytest.mark.asyncio
async def test_exist_true(mock_session):
    """Test exist returns True if country exists."""
    mock_result = AsyncMock()
    mock_result.scalar_one_or_none = MagicMock(return_value="US")
    mock_session.execute = AsyncMock(return_value=mock_result)

    repo = SQLAlchemyCountryRepository(mock_session)
    exists = await repo.exist("US")

    assert exists is True


@pytest.mark.asyncio
async def test_exist_false(mock_session):
    """Test exist returns False if country does not exist."""
    mock_result = AsyncMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=None)
    mock_session.execute = AsyncMock(return_value=mock_result)

    repo = SQLAlchemyCountryRepository(mock_session)
    exists = await repo.exist("XX")

    assert exists is False


@pytest.mark.asyncio
async def test_exist_error(mock_session):
    """Test exist raises DatabaseTimeoutError on timeout."""
    mock_session.execute = AsyncMock(side_effect=SATimeoutError("timeout"))
    repo = SQLAlchemyCountryRepository(mock_session)

    with pytest.raises(DatabaseTimeoutError):
        await repo.exist("US")