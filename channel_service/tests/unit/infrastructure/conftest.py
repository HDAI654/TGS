"""Pytest configuration and shared fixtures."""

import pytest
from unittest.mock import AsyncMock, MagicMock, Mock
from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.persistence.postgres.postgres_channel_repo import (
    SQLAlchemyChannelRepository,
)
from src.infrastructure.persistence.postgres.postgres_country_repo import (
    SQLAlchemyCountryRepository,
)


@pytest.fixture
def mock_session():
    """Create a mock AsyncSession."""
    session = AsyncMock(spec=AsyncSession)
    session.execute = AsyncMock()
    return session


@pytest.fixture
def mock_channel_repo(mock_session):
    """Create a mock channel repository with mock session."""
    return SQLAlchemyChannelRepository(mock_session)


@pytest.fixture
def mock_country_repo(mock_session):
    """Create a mock country repository with mock session."""
    return SQLAlchemyCountryRepository(mock_session)


@pytest.fixture
def mock_result():
    """Create a mock result object."""
    result = Mock()
    result.scalar_one_or_none = Mock()
    result.scalars = Mock()
    result.all = Mock()
    result.scalar = Mock()
    return result


@pytest.fixture
def mock_scalar_result():
    """Create a mock result for scalar queries."""
    result = Mock()
    result.scalar_one = Mock()
    result.scalar = Mock()
    return result
