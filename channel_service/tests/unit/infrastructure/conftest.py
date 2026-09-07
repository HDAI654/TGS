"""Shared test fixtures for repository tests."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.persistence.models import (
    CategoryModel,
    ChannelModel,
    CountryModel,
)


@pytest.fixture
def mock_session() -> AsyncMock:
    """Return a mock AsyncSession with async execute method."""
    session = AsyncMock(spec=AsyncSession)
    # Default execute returns a mock that can be chained
    mock_result = AsyncMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=None)
    mock_result.scalars = MagicMock(return_value=AsyncMock())
    mock_result.scalars.return_value.all = MagicMock(return_value=[])
    session.execute = AsyncMock(return_value=mock_result)
    return session


@pytest.fixture
def sample_category_model() -> CategoryModel:
    return CategoryModel(id=1, name="News")


@pytest.fixture
def sample_country_model() -> CountryModel:
    return CountryModel(
        country_code="US",
        country_name="United States",
        timezone="America/New_York",
        has_channels=True,
        channel_count=10,
    )


@pytest.fixture
def sample_channel_model(sample_category_model, sample_country_model) -> ChannelModel:
    return ChannelModel(
        id="12345678-1234-1234-1234-123456789abc",
        name="CNN",
        category=sample_category_model,
        country=sample_country_model,
        language="en",
        country_code="US",
        urls={"urls": ["https://cnn.com"]},
        category_id=1,
    )
