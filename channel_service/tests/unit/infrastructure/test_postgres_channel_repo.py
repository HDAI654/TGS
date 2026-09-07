"""Unit tests for SQLAlchemyChannelRepository."""

import pytest
from uuid import uuid4
from unittest.mock import MagicMock
from sqlalchemy.exc import (
    IntegrityError,
    OperationalError,
    SQLAlchemyError,
    TimeoutError,
)
from src.domain.entities.channel import Channel
from src.domain.entities.category import Category
from src.infrastructure.persistence.models import ChannelModel
from src.exceptions.infrastructure import (
    DatabaseConnectionError,
    DatabaseOperationError,
    DatabaseTimeoutError,
)


@pytest.fixture
def sample_channel():
    return Channel(
        id=uuid4(),
        name="CNN",
        category=Category(id=1, name="News"),
        language="en",
        country_code="US",
        urls=("https://cnn.com",),
    )


@pytest.fixture
def sample_channel_model(sample_channel):
    """Create a mock ChannelModel with relationships."""
    model = MagicMock(spec=ChannelModel)
    model.id = sample_channel.id
    model.name = sample_channel.name
    model.language = sample_channel.language
    model.country_code = sample_channel.country_code
    model.urls = list(sample_channel.urls)
    model.category = MagicMock()
    model.category.id = sample_channel.category.id
    model.category.name = sample_channel.category.name
    model.country = MagicMock()
    model.country.country_code = sample_channel.country_code
    return model


class TestSQLAlchemyChannelRepository:
    """Tests for SQLAlchemyChannelRepository."""

    @pytest.mark.asyncio
    async def test_get_by_id_found(
        self, mock_channel_repo, mock_session, sample_channel, sample_channel_model
    ):
        """Should return channel when found."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_channel_model
        mock_session.execute.return_value = mock_result

        result = await mock_channel_repo.get_by_id(sample_channel.id)

        assert result is not None
        assert result.id == sample_channel.id
        assert result.name == sample_channel.name
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, mock_channel_repo, mock_session):
        """Should return None when channel not found."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        result = await mock_channel_repo.get_by_id(uuid4())

        assert result is None
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_id_db_error(self, mock_channel_repo, mock_session):
        """Should raise DatabaseOperationError on SQLAlchemy error."""
        mock_session.execute.side_effect = SQLAlchemyError("DB error")

        with pytest.raises(DatabaseOperationError) as exc_info:
            await mock_channel_repo.get_by_id(uuid4())
        assert "Database operation failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_by_id_timeout(self, mock_channel_repo, mock_session):
        """Should raise DatabaseTimeoutError on timeout."""
        mock_session.execute.side_effect = TimeoutError("Timeout")

        with pytest.raises(DatabaseTimeoutError) as exc_info:
            await mock_channel_repo.get_by_id(uuid4())
        assert "timed out" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_by_id_connection_error(self, mock_channel_repo, mock_session):
        """Should raise DatabaseConnectionError on connection error."""
        mock_session.execute.side_effect = OperationalError(
            "Connection failed", None, None
        )

        with pytest.raises(DatabaseConnectionError) as exc_info:
            await mock_channel_repo.get_by_id(uuid4())
        assert "connect" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_get_all_success(
        self, mock_channel_repo, mock_session, sample_channel_model
    ):
        """Should return all channels."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_channel_model]
        mock_session.execute.return_value = mock_result

        results = await mock_channel_repo.get_all()

        assert len(results) == 1
        assert results[0].name == sample_channel_model.name
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_all_empty(self, mock_channel_repo, mock_session):
        """Should return empty list when no channels."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute.return_value = mock_result

        results = await mock_channel_repo.get_all()

        assert results == []
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_all_db_error(self, mock_channel_repo, mock_session):
        """Should raise DatabaseOperationError on SQLAlchemy error."""
        mock_session.execute.side_effect = SQLAlchemyError("DB error")

        with pytest.raises(DatabaseOperationError):
            await mock_channel_repo.get_all()

    @pytest.mark.asyncio
    async def test_search_success(
        self, mock_channel_repo, mock_session, sample_channel_model
    ):
        """Should return search results with total count."""
        mock_count_result = MagicMock()
        mock_count_result.scalar_one.return_value = 1

        mock_search_result = MagicMock()
        mock_search_result.scalars.return_value.all.return_value = [
            sample_channel_model
        ]

        mock_session.execute.side_effect = [mock_count_result, mock_search_result]

        results, total = await mock_channel_repo.search("test", 10, 0)

        assert len(results) == 1
        assert total == 1
        assert results[0].name == sample_channel_model.name
        assert mock_session.execute.call_count == 2

    @pytest.mark.asyncio
    async def test_search_no_results(self, mock_channel_repo, mock_session):
        """Should return empty list when no matches found."""
        mock_count_result = MagicMock()
        mock_count_result.scalar_one.return_value = 0

        mock_search_result = MagicMock()
        mock_search_result.scalars.return_value.all.return_value = []

        mock_session.execute.side_effect = [mock_count_result, mock_search_result]

        results, total = await mock_channel_repo.search("nonexistent", 10, 0)

        assert results == []
        assert total == 0
        assert mock_session.execute.call_count == 2

    @pytest.mark.asyncio
    async def test_search_count_error(self, mock_channel_repo, mock_session):
        """Should raise error when count query fails."""
        mock_session.execute.side_effect = SQLAlchemyError("Count failed")

        with pytest.raises(DatabaseOperationError):
            await mock_channel_repo.search("test", 10, 0)

    @pytest.mark.asyncio
    async def test_search_main_query_error(self, mock_channel_repo, mock_session):
        """Should raise error when main search query fails."""
        mock_count_result = MagicMock()
        mock_count_result.scalar_one.return_value = 1
        mock_session.execute.side_effect = [
            mock_count_result,
            SQLAlchemyError("Search failed"),
        ]

        with pytest.raises(DatabaseOperationError):
            await mock_channel_repo.search("test", 10, 0)

    @pytest.mark.asyncio
    async def test_search_with_pagination(
        self, mock_channel_repo, mock_session, sample_channel_model
    ):
        """Should respect pagination parameters."""
        mock_count_result = MagicMock()
        mock_count_result.scalar_one.return_value = 2

        mock_search_result = MagicMock()
        mock_search_result.scalars.return_value.all.return_value = [
            sample_channel_model
        ]

        mock_session.execute.side_effect = [mock_count_result, mock_search_result]

        results, total = await mock_channel_repo.search("test", 1, 1)

        assert len(results) == 1
        assert total == 2
        mock_session.execute.assert_called()

    @pytest.mark.asyncio
    async def test_exist_true(self, mock_channel_repo, mock_session):
        """Should return True when channel exists."""
        mock_result = MagicMock()
        mock_result.scalar.return_value = True
        mock_session.execute.return_value = mock_result

        result = await mock_channel_repo.exist(uuid4())

        assert result is True
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_exist_false(self, mock_channel_repo, mock_session):
        """Should return False when channel doesn't exist."""
        mock_result = MagicMock()
        mock_result.scalar.return_value = False
        mock_session.execute.return_value = mock_result

        result = await mock_channel_repo.exist(uuid4())

        assert result is False
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_exist_db_error(self, mock_channel_repo, mock_session):
        """Should raise DatabaseOperationError on SQLAlchemy error."""
        mock_session.execute.side_effect = SQLAlchemyError("DB error")

        with pytest.raises(DatabaseOperationError):
            await mock_channel_repo.exist(uuid4())

    @pytest.mark.asyncio
    async def test_execute_db_operation_integrity_error(self, mock_channel_repo):
        """Should handle IntegrityError."""

        async def failing_coro(*args, **kwargs):
            raise IntegrityError("Integrity violation", None, None)

        with pytest.raises(DatabaseOperationError) as exc_info:
            await mock_channel_repo._execute_db_operation(
                "test_operation", failing_coro
            )
        assert "integrity error" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_execute_db_operation_operational_error(self, mock_channel_repo):
        """Should handle OperationalError."""

        async def failing_coro(*args, **kwargs):
            raise OperationalError("Connection failed", None, None)

        with pytest.raises(DatabaseConnectionError):
            await mock_channel_repo._execute_db_operation(
                "test_operation", failing_coro
            )

    @pytest.mark.asyncio
    async def test_execute_db_operation_timeout_error(self, mock_channel_repo):
        """Should handle TimeoutError."""

        async def failing_coro(*args, **kwargs):
            raise TimeoutError("Timeout")

        with pytest.raises(DatabaseTimeoutError):
            await mock_channel_repo._execute_db_operation(
                "test_operation", failing_coro
            )
