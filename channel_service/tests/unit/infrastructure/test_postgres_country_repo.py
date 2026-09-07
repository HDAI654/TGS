"""Unit tests for SQLAlchemyCountryRepository."""

import pytest
from unittest.mock import MagicMock
from sqlalchemy.exc import (
    IntegrityError,
    OperationalError,
    SQLAlchemyError,
    TimeoutError,
)
from src.domain.entities.country import Country
from src.exceptions.infrastructure import (
    DatabaseConnectionError,
    DatabaseOperationError,
    DatabaseTimeoutError,
)
from src.infrastructure.persistence.models import CountryModel


@pytest.fixture
def sample_country():
    return Country(
        country_code="US",
        country_name="United States",
        timezone="America/New_York",
        has_channels=True,
        channel_count=3,
    )


@pytest.fixture
def sample_country_model(sample_country):
    """Create a mock CountryModel."""
    model = MagicMock(spec=CountryModel)
    model.country_code = sample_country.country_code
    model.country_name = sample_country.country_name
    model.timezone = sample_country.timezone
    model.has_channels = sample_country.has_channels
    model.channel_count = sample_country.channel_count
    return model


class TestSQLAlchemyCountryRepository:
    """Tests for SQLAlchemyCountryRepository."""

    @pytest.mark.asyncio
    async def test_get_by_id_found(
        self, mock_country_repo, mock_session, sample_country, sample_country_model
    ):
        """Should return country when found."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_country_model
        mock_session.execute.return_value = mock_result

        result = await mock_country_repo.get_by_id(sample_country.country_code)

        assert result is not None
        assert result.country_code == sample_country.country_code
        assert result.country_name == sample_country.country_name
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, mock_country_repo, mock_session):
        """Should return None when country not found."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        result = await mock_country_repo.get_by_id("XX")

        assert result is None
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_id_db_error(self, mock_country_repo, mock_session):
        """Should raise DatabaseOperationError on SQLAlchemy error."""
        mock_session.execute.side_effect = SQLAlchemyError("DB error")

        with pytest.raises(DatabaseOperationError) as exc_info:
            await mock_country_repo.get_by_id("US")
        assert "Database operation failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_by_id_timeout(self, mock_country_repo, mock_session):
        """Should raise DatabaseTimeoutError on timeout."""
        mock_session.execute.side_effect = TimeoutError("Timeout")

        with pytest.raises(DatabaseTimeoutError) as exc_info:
            await mock_country_repo.get_by_id("US")
        assert "timed out" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_by_id_connection_error(self, mock_country_repo, mock_session):
        """Should raise DatabaseConnectionError on connection error."""
        mock_session.execute.side_effect = OperationalError(
            "Connection failed", None, None
        )

        with pytest.raises(DatabaseConnectionError) as exc_info:
            await mock_country_repo.get_by_id("US")
        assert "connect" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_get_all_success(
        self, mock_country_repo, mock_session, sample_country_model
    ):
        """Should return all countries."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_country_model]
        mock_session.execute.return_value = mock_result

        results = await mock_country_repo.get_all()

        assert len(results) == 1
        assert results[0].country_code == sample_country_model.country_code
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_all_empty(self, mock_country_repo, mock_session):
        """Should return empty list when no countries."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute.return_value = mock_result

        results = await mock_country_repo.get_all()

        assert results == []
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_all_db_error(self, mock_country_repo, mock_session):
        """Should raise DatabaseOperationError on SQLAlchemy error."""
        mock_session.execute.side_effect = SQLAlchemyError("DB error")

        with pytest.raises(DatabaseOperationError):
            await mock_country_repo.get_all()

    @pytest.mark.asyncio
    async def test_search_success(
        self, mock_country_repo, mock_session, sample_country_model
    ):
        """Should return search results with total count."""
        mock_count_result = MagicMock()
        mock_count_result.scalar_one.return_value = 1

        mock_search_result = MagicMock()
        mock_search_result.scalars.return_value.all.return_value = [
            sample_country_model
        ]

        mock_session.execute.side_effect = [mock_count_result, mock_search_result]

        results, total = await mock_country_repo.search("US", 10, 0)

        assert len(results) == 1
        assert total == 1
        assert results[0].country_code == sample_country_model.country_code
        assert mock_session.execute.call_count == 2

    @pytest.mark.asyncio
    async def test_search_no_results(self, mock_country_repo, mock_session):
        """Should return empty list when no matches found."""
        mock_count_result = MagicMock()
        mock_count_result.scalar_one.return_value = 0

        mock_search_result = MagicMock()
        mock_search_result.scalars.return_value.all.return_value = []

        mock_session.execute.side_effect = [mock_count_result, mock_search_result]

        results, total = await mock_country_repo.search("nonexistent", 10, 0)

        assert results == []
        assert total == 0
        assert mock_session.execute.call_count == 2

    @pytest.mark.asyncio
    async def test_search_count_error(self, mock_country_repo, mock_session):
        """Should raise error when count query fails."""
        mock_session.execute.side_effect = SQLAlchemyError("Count failed")

        with pytest.raises(DatabaseOperationError):
            await mock_country_repo.search("US", 10, 0)

    @pytest.mark.asyncio
    async def test_search_main_query_error(self, mock_country_repo, mock_session):
        """Should raise error when main search query fails."""
        mock_count_result = MagicMock()
        mock_count_result.scalar_one.return_value = 1
        mock_session.execute.side_effect = [
            mock_count_result,
            SQLAlchemyError("Search failed"),
        ]

        with pytest.raises(DatabaseOperationError):
            await mock_country_repo.search("US", 10, 0)

    @pytest.mark.asyncio
    async def test_search_with_pagination(
        self, mock_country_repo, mock_session, sample_country_model
    ):
        """Should respect pagination parameters."""
        mock_count_result = MagicMock()
        mock_count_result.scalar_one.return_value = 2

        mock_search_result = MagicMock()
        mock_search_result.scalars.return_value.all.return_value = [
            sample_country_model
        ]

        mock_session.execute.side_effect = [mock_count_result, mock_search_result]

        results, total = await mock_country_repo.search("a", 1, 1)

        assert len(results) == 1
        assert total == 2
        mock_session.execute.assert_called()

    @pytest.mark.asyncio
    async def test_search_by_name(
        self, mock_country_repo, mock_session, sample_country_model
    ):
        """Should search by country name."""
        mock_count_result = MagicMock()
        mock_count_result.scalar_one.return_value = 1

        mock_search_result = MagicMock()
        mock_search_result.scalars.return_value.all.return_value = [
            sample_country_model
        ]

        mock_session.execute.side_effect = [mock_count_result, mock_search_result]

        results, total = await mock_country_repo.search("United", 10, 0)

        assert len(results) == 1
        assert total == 1
        assert results[0].country_name == "United States"

    @pytest.mark.asyncio
    async def test_search_by_timezone(
        self, mock_country_repo, mock_session, sample_country_model
    ):
        """Should search by timezone."""
        mock_count_result = MagicMock()
        mock_count_result.scalar_one.return_value = 1

        mock_search_result = MagicMock()
        mock_search_result.scalars.return_value.all.return_value = [
            sample_country_model
        ]

        mock_session.execute.side_effect = [mock_count_result, mock_search_result]

        results, total = await mock_country_repo.search("America", 10, 0)

        assert len(results) == 1
        assert total == 1
        assert results[0].timezone == "America/New_York"

    @pytest.mark.asyncio
    async def test_exist_true(self, mock_country_repo, mock_session):
        """Should return True when country exists."""
        mock_result = MagicMock()
        mock_result.scalar.return_value = True
        mock_session.execute.return_value = mock_result

        result = await mock_country_repo.exist("US")

        assert result is True
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_exist_false(self, mock_country_repo, mock_session):
        """Should return False when country doesn't exist."""
        mock_result = MagicMock()
        mock_result.scalar.return_value = False
        mock_session.execute.return_value = mock_result

        result = await mock_country_repo.exist("XX")

        assert result is False
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_exist_db_error(self, mock_country_repo, mock_session):
        """Should raise DatabaseOperationError on SQLAlchemy error."""
        mock_session.execute.side_effect = SQLAlchemyError("DB error")

        with pytest.raises(DatabaseOperationError):
            await mock_country_repo.exist("US")

    @pytest.mark.asyncio
    async def test_execute_db_operation_integrity_error(self, mock_country_repo):
        """Should handle IntegrityError."""

        async def failing_coro(*args, **kwargs):
            raise IntegrityError("Integrity violation", None, None)

        with pytest.raises(DatabaseOperationError) as exc_info:
            await mock_country_repo._execute_db_operation(
                "test_operation", failing_coro
            )
        assert "integrity error" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_execute_db_operation_operational_error(self, mock_country_repo):
        """Should handle OperationalError."""

        async def failing_coro(*args, **kwargs):
            raise OperationalError("Connection failed", None, None)

        with pytest.raises(DatabaseConnectionError):
            await mock_country_repo._execute_db_operation(
                "test_operation", failing_coro
            )

    @pytest.mark.asyncio
    async def test_execute_db_operation_timeout_error(self, mock_country_repo):
        """Should handle TimeoutError."""

        async def failing_coro(*args, **kwargs):
            raise TimeoutError("Timeout")

        with pytest.raises(DatabaseTimeoutError):
            await mock_country_repo._execute_db_operation(
                "test_operation", failing_coro
            )

    @pytest.mark.asyncio
    async def test_execute_db_operation_unexpected_error(self, mock_country_repo):
        """Should handle unexpected errors."""

        async def failing_coro(*args, **kwargs):
            raise ValueError("Unexpected error")

        with pytest.raises(DatabaseOperationError) as exc_info:
            await mock_country_repo._execute_db_operation(
                "test_operation", failing_coro
            )
        assert "Unexpected database error" in str(exc_info.value)
