import pytest
from unittest.mock import AsyncMock, MagicMock


@pytest.fixture
def mock_country_repo():
    return AsyncMock()


@pytest.fixture
def mock_channel_repo():
    return AsyncMock()


@pytest.fixture
def mock_uow(mock_country_repo, mock_channel_repo):
    uow = AsyncMock()
    uow.countries = mock_country_repo
    uow.channels = mock_channel_repo
    return uow


@pytest.fixture
def mock_crawler():
    return AsyncMock()
