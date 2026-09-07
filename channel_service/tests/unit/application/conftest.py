import pytest
from uuid import uuid4
from src.domain.entities.channel import Channel
from src.domain.entities.category import Category
from src.domain.entities.country import Country


class MockChannelRepository:
    """Mock repository for Channel queries."""
    def __init__(self):
        self.get_by_id_return = None
        self.search_return = ([], 0)
        self.get_by_id_called_with = None
        self.search_called_with = None

    async def get_by_id(self, channel_id):
        self.get_by_id_called_with = channel_id
        return self.get_by_id_return

    async def search(self, text, limit, offset):
        self.search_called_with = (text, limit, offset)
        return self.search_return


class MockCountryRepository:
    """Mock repository for Country queries."""
    def __init__(self):
        self.get_by_id_return = None
        self.search_return = ([], 0)
        self.get_by_id_called_with = None
        self.search_called_with = None

    async def get_by_id(self, country_code):
        self.get_by_id_called_with = country_code
        return self.get_by_id_return

    async def search(self, text, limit, offset):
        self.search_called_with = (text, limit, offset)
        return self.search_return


@pytest.fixture
def mock_channel_repo():
    return MockChannelRepository()


@pytest.fixture
def mock_country_repo():
    return MockCountryRepository()

@pytest.fixture
def sample_category():
    return Category(
        id=0, 
        name="Sport",
    )

@pytest.fixture
def sample_channel(sample_category):
    return Channel(
        id=uuid4(), 
        name="Test Channel", 
        category=sample_category,
        language="eng",
        country_code="US",
        urls=("https://example.com"),
    )


@pytest.fixture
def sample_country():
    return Country(
        country_code="US",
        country_name="United States of America",
        timezone="America/New_York",
        has_channels=True,
        channel_count=1,
    )