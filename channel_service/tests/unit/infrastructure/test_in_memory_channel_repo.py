"""Unit tests for InMemoryChannelRepository."""

import pytest
from uuid import uuid4
from src.domain.entities.channel import Channel
from src.domain.entities.category import Category
from src.infrastructure.persistence.in_memory.in_memory_channel_repo import (
    InMemoryChannelRepository,
)


@pytest.fixture
def sample_category():
    return Category(id=1, name="News")


@pytest.fixture
def sample_channels(sample_category):
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
            category=sample_category,
            language="ar",
            country_code="QA",
            urls=("https://aljazeera.com",),
        ),
        Channel(
            id=uuid4(),
            name="ESPN",
            category=Category(id=2, name="Sports"),
            language="en",
            country_code="US",
            urls=("https://espn.com",),
        ),
    ]


@pytest.fixture
def country_name_map():
    return {
        "US": "United States",
        "GB": "United Kingdom",
        "QA": "Qatar",
    }


@pytest.fixture
def repo(sample_channels, country_name_map):
    return InMemoryChannelRepository(
        channels=sample_channels,
        country_name_map=country_name_map,
    )


class TestInMemoryChannelRepository:
    """Tests for InMemoryChannelRepository."""

    @pytest.mark.asyncio
    async def test_get_by_id_found(self, repo, sample_channels):
        """Should return channel when it exists."""
        channel = sample_channels[0]
        result = await repo.get_by_id(channel.id)
        assert result == channel
        assert result.id == channel.id
        assert result.name == channel.name

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, repo):
        """Should return None when channel doesn't exist."""
        fake_id = uuid4()
        result = await repo.get_by_id(fake_id)
        assert result is None

    @pytest.mark.asyncio
    async def test_get_all(self, repo, sample_channels):
        """Should return all channels."""
        results = await repo.get_all()
        assert len(results) == len(sample_channels)
        assert set(c.id for c in results) == set(c.id for c in sample_channels)

    @pytest.mark.asyncio
    async def test_get_all_empty(self):
        """Should return empty list when no channels."""
        repo = InMemoryChannelRepository()
        results = await repo.get_all()
        assert results == []

    @pytest.mark.asyncio
    async def test_search_by_name(self, repo):
        """Should search channels by name."""
        results, total = await repo.search("CNN", 10, 0)
        assert total == 1
        assert len(results) == 1
        assert results[0].name == "CNN"

    @pytest.mark.asyncio
    async def test_search_by_name_case_insensitive(self, repo):
        """Should search channels by name case-insensitively."""
        results, total = await repo.search("cnn", 10, 0)
        assert total == 1
        assert len(results) == 1
        assert results[0].name == "CNN"

    @pytest.mark.asyncio
    async def test_search_by_category_name(self, repo):
        """Should search channels by category name."""
        results, total = await repo.search("News", 10, 0)
        assert total == 3  # CNN, BBC, Al Jazeera
        assert len(results) == 3
        assert all(c.category.name == "News" for c in results)

    @pytest.mark.asyncio
    async def test_search_by_language(self, repo):
        """Should search channels by language."""
        results, total = await repo.search("ar", 10, 0)
        assert total == 1
        assert len(results) == 1
        assert results[0].language == "ar"
        assert results[0].name == "Al Jazeera"

    @pytest.mark.asyncio
    async def test_search_by_country_code(self, repo):
        """Should search channels by country code."""
        results, total = await repo.search("US", 10, 0)
        assert total == 2  # CNN, ESPN
        assert len(results) == 2
        assert all(c.country_code == "US" for c in results)

    @pytest.mark.asyncio
    async def test_search_by_country_name(self, repo, country_name_map):
        """Should search channels by country name."""
        results, total = await repo.search("United", 10, 0)
        assert (
            total == 3
        )  # CNN (US), ESPN (US), BBC (GB) - all have "United" in country name
        assert len(results) == 3

    @pytest.mark.asyncio
    async def test_search_no_results(self, repo):
        """Should return empty list when no matches found."""
        results, total = await repo.search("Nonexistent", 10, 0)
        assert total == 0
        assert len(results) == 0

    @pytest.mark.asyncio
    async def test_search_pagination_first_page(self, repo):
        """Should return first page of results."""
        results, total = await repo.search("e", 2, 0)  # 'e' matches many channels
        assert total == 4  # All channels have 'e' in name
        assert len(results) == 2
        # Should be sorted by name: Al Jazeera, BBC, CNN, ESPN
        assert results[0].name == "Al Jazeera"
        assert results[1].name == "BBC World"

    @pytest.mark.asyncio
    async def test_search_pagination_second_page(self, repo):
        """Should return second page of results."""
        results, total = await repo.search("e", 2, 2)
        assert total == 4
        assert len(results) == 2
        # Second page should be: CNN, ESPN
        assert results[0].name == "CNN"
        assert results[1].name == "ESPN"

    @pytest.mark.asyncio
    async def test_search_pagination_offset_beyond_results(self, repo):
        """Should return empty list when offset exceeds total."""
        results, total = await repo.search("e", 10, 10)
        assert total == 4
        assert len(results) == 0

    @pytest.mark.asyncio
    async def test_search_sort_order(self, repo):
        """Should return results sorted by name then id."""
        results, total = await repo.search("e", 10, 0)
        assert total == 4
        names = [c.name for c in results]
        assert names == sorted(names)  # Check alphabetical order

    @pytest.mark.asyncio
    async def test_exist_true(self, repo, sample_channels):
        """Should return True when channel exists."""
        channel = sample_channels[0]
        result = await repo.exist(channel.id)
        assert result is True

    @pytest.mark.asyncio
    async def test_exist_false(self, repo):
        """Should return False when channel doesn't exist."""
        fake_id = uuid4()
        result = await repo.exist(fake_id)
        assert result is False

    @pytest.mark.asyncio
    async def test_repository_with_empty_channels(self):
        """Should handle empty channel list."""
        repo = InMemoryChannelRepository(channels=[])
        results = await repo.get_all()
        assert results == []

        result = await repo.get_by_id(uuid4())
        assert result is None

        results, total = await repo.search("test", 10, 0)
        assert total == 0
        assert len(results) == 0

        exists = await repo.exist(uuid4())
        assert exists is False

    @pytest.mark.asyncio
    async def test_repository_with_no_country_map(self, sample_channels):
        """Should handle missing country name map."""
        repo = InMemoryChannelRepository(channels=sample_channels)
        results, total = await repo.search("United", 10, 0)
        assert total == 0  # No country names to match
        assert len(results) == 0
