"""Unit tests for InMemoryChannelRepository and InMemoryCountryRepository."""

import pytest
from uuid import uuid4

from src.domain.entities.channel import Channel, Category
from src.domain.entities.country import Country
from src.infrastructure.persistence.in_memory_repos import (
    InMemoryChannelRepository,
    InMemoryCountryRepository,
)


@pytest.fixture
def sample_category() -> Category:
    return Category(id=1, name="News")


@pytest.fixture
def sample_channels(sample_category) -> list[Channel]:
    return [
        Channel(
            id=uuid4(),
            name="CNN",
            category=sample_category,
            language="en",
            country_code="US",
            urls=("https://cnn.com",),
        ),
        Channel(
            id=uuid4(),
            name="BBC World",
            category=sample_category,
            language="en",
            country_code="GB",
            urls=("https://bbc.com",),
        ),
        Channel(
            id=uuid4(),
            name="Al Jazeera",
            category=Category(id=2, name="International"),
            language="ar",
            country_code="QA",
            urls=("https://aljazeera.com",),
        ),
    ]


@pytest.fixture
def sample_countries() -> list[Country]:
    return [
        Country(
            country_code="US",
            country_name="United States",
            timezone="America/New_York",
            has_channels=True,
            channel_count=5,
        ),
        Country(
            country_code="GB",
            country_name="United Kingdom",
            timezone="Europe/London",
            has_channels=True,
            channel_count=3,
        ),
        Country(
            country_code="QA",
            country_name="Qatar",
            timezone="Asia/Qatar",
            has_channels=True,
            channel_count=2,
        ),
    ]


# ---- Channel Repository Tests ----


@pytest.mark.asyncio
async def test_channel_get_by_id_found(sample_channels):
    repo = InMemoryChannelRepository(sample_channels)
    target = sample_channels[0]
    result = await repo.get_by_id(target.id)
    assert result == target


@pytest.mark.asyncio
async def test_channel_get_by_id_not_found(sample_channels):
    repo = InMemoryChannelRepository(sample_channels)
    result = await repo.get_by_id(uuid4())
    assert result is None


@pytest.mark.asyncio
async def test_channel_get_all(sample_channels):
    repo = InMemoryChannelRepository(sample_channels)
    results = await repo.get_all()
    assert len(results) == 3
    assert set(c.id for c in results) == set(c.id for c in sample_channels)


@pytest.mark.asyncio
async def test_channel_search_by_name(sample_channels):
    repo = InMemoryChannelRepository(sample_channels)
    results, total = await repo.search("CNN", limit=10, offset=0)
    assert total == 1
    assert results[0].name == "CNN"


@pytest.mark.asyncio
async def test_channel_search_case_insensitive(sample_channels):
    repo = InMemoryChannelRepository(sample_channels)
    results, total = await repo.search("cnn", limit=10, offset=0)
    assert total == 1
    assert results[0].name == "CNN"


@pytest.mark.asyncio
async def test_channel_search_by_category_name(sample_channels):
    repo = InMemoryChannelRepository(sample_channels)
    results, total = await repo.search("news", limit=10, offset=0)
    # Should match CNN and BBC World (both category "News")
    assert total == 2
    names = {c.name for c in results}
    assert "CNN" in names and "BBC World" in names


@pytest.mark.asyncio
async def test_channel_search_by_country_name(sample_channels):
    country_name_map = {"US": "United States", "GB": "United Kingdom", "QA": "Qatar"}
    repo = InMemoryChannelRepository(sample_channels, country_name_map=country_name_map)
    results, total = await repo.search("united", limit=10, offset=0)
    # Should match US and GB countries => CNN and BBC World
    assert total == 2
    names = {c.name for c in results}
    assert "CNN" in names and "BBC World" in names


@pytest.mark.asyncio
async def test_channel_search_by_language(sample_channels):
    repo = InMemoryChannelRepository(sample_channels)
    results, total = await repo.search("ar", limit=10, offset=0)
    assert total == 1
    assert results[0].name == "Al Jazeera"


@pytest.mark.asyncio
async def test_channel_search_by_country_code(sample_channels):
    repo = InMemoryChannelRepository(sample_channels)
    results, total = await repo.search("gb", limit=10, offset=0)
    assert total == 1
    assert results[0].country_code == "GB"


@pytest.mark.asyncio
async def test_channel_search_empty(sample_channels):
    repo = InMemoryChannelRepository(sample_channels)
    results, total = await repo.search("xyz", limit=10, offset=0)
    assert total == 0
    assert results == []


@pytest.mark.asyncio
async def test_channel_search_pagination(sample_channels):
    repo = InMemoryChannelRepository(sample_channels)
    # All channels sorted by name, then id: Al Jazeera, BBC World, CNN
    results, total = await repo.search("", limit=2, offset=0)
    assert total == 3
    assert len(results) == 2
    assert results[0].name == "Al Jazeera"
    assert results[1].name == "BBC World"

    results, total = await repo.search("", limit=2, offset=2)
    assert len(results) == 1
    assert results[0].name == "CNN"


@pytest.mark.asyncio
async def test_channel_exist_true(sample_channels):
    repo = InMemoryChannelRepository(sample_channels)
    assert await repo.exist(sample_channels[0].id) is True


@pytest.mark.asyncio
async def test_channel_exist_false(sample_channels):
    repo = InMemoryChannelRepository(sample_channels)
    assert await repo.exist(uuid4()) is False


# ---- Country Repository Tests ----


@pytest.mark.asyncio
async def test_country_get_by_id_found(sample_countries):
    repo = InMemoryCountryRepository(sample_countries)
    target = sample_countries[0]
    result = await repo.get_by_id(target.country_code)
    assert result == target


@pytest.mark.asyncio
async def test_country_get_by_id_not_found(sample_countries):
    repo = InMemoryCountryRepository(sample_countries)
    result = await repo.get_by_id("XX")
    assert result is None


@pytest.mark.asyncio
async def test_country_get_all(sample_countries):
    repo = InMemoryCountryRepository(sample_countries)
    results = await repo.get_all()
    assert len(results) == 3
    assert set(c.country_code for c in results) == {"US", "GB", "QA"}


@pytest.mark.asyncio
async def test_country_search_by_code(sample_countries):
    repo = InMemoryCountryRepository(sample_countries)
    results, total = await repo.search("us", limit=10, offset=0)
    assert total == 1
    assert results[0].country_code == "US"


@pytest.mark.asyncio
async def test_country_search_by_name(sample_countries):
    repo = InMemoryCountryRepository(sample_countries)
    results, total = await repo.search("united", limit=10, offset=0)
    assert total == 2  # United States and United Kingdom
    codes = {c.country_code for c in results}
    assert "US" in codes and "GB" in codes


@pytest.mark.asyncio
async def test_country_search_by_timezone(sample_countries):
    repo = InMemoryCountryRepository(sample_countries)
    results, total = await repo.search("asia", limit=10, offset=0)
    assert total == 1
    assert results[0].country_code == "QA"


@pytest.mark.asyncio
async def test_country_search_case_insensitive(sample_countries):
    repo = InMemoryCountryRepository(sample_countries)
    results, total = await repo.search("qatar", limit=10, offset=0)
    assert total == 1
    assert results[0].country_code == "QA"


@pytest.mark.asyncio
async def test_country_search_empty(sample_countries):
    repo = InMemoryCountryRepository(sample_countries)
    results, total = await repo.search("xyz", limit=10, offset=0)
    assert total == 0
    assert results == []


@pytest.mark.asyncio
async def test_country_search_pagination(sample_countries):
    repo = InMemoryCountryRepository(sample_countries)
    # Sorted by country_code: GB, QA, US
    results, total = await repo.search("", limit=2, offset=0)
    assert total == 3
    assert len(results) == 2
    assert results[0].country_code == "GB"
    assert results[1].country_code == "QA"

    results, total = await repo.search("", limit=2, offset=2)
    assert len(results) == 1
    assert results[0].country_code == "US"


@pytest.mark.asyncio
async def test_country_exist_true(sample_countries):
    repo = InMemoryCountryRepository(sample_countries)
    assert await repo.exist("US") is True


@pytest.mark.asyncio
async def test_country_exist_false(sample_countries):
    repo = InMemoryCountryRepository(sample_countries)
    assert await repo.exist("XX") is False
