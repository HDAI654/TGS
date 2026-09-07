"""Unit tests for InMemoryCountryRepository."""

import pytest
from src.domain.entities.country import Country
from src.infrastructure.persistence.in_memory.in_memory_country_repo import (
    InMemoryCountryRepository,
)


@pytest.fixture
def sample_countries():
    return [
        Country(
            country_code="US",
            country_name="United States",
            timezone="America/New_York",
            has_channels=True,
            channel_count=3,
        ),
        Country(
            country_code="GB",
            country_name="United Kingdom",
            timezone="Europe/London",
            has_channels=True,
            channel_count=1,
        ),
        Country(
            country_code="QA",
            country_name="Qatar",
            timezone="Asia/Qatar",
            has_channels=True,
            channel_count=1,
        ),
        Country(
            country_code="FR",
            country_name="France",
            timezone="Europe/Paris",
            has_channels=False,
            channel_count=0,
        ),
    ]


@pytest.fixture
def repo(sample_countries):
    return InMemoryCountryRepository(countries=sample_countries)


class TestInMemoryCountryRepository:
    """Tests for InMemoryCountryRepository."""

    @pytest.mark.asyncio
    async def test_get_by_id_found(self, repo, sample_countries):
        """Should return country when it exists."""
        country = sample_countries[0]
        result = await repo.get_by_id(country.country_code)
        assert result == country
        assert result.country_code == country.country_code
        assert result.country_name == country.country_name

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, repo):
        """Should return None when country doesn't exist."""
        result = await repo.get_by_id("XX")
        assert result is None

    @pytest.mark.asyncio
    async def test_get_all(self, repo, sample_countries):
        """Should return all countries."""
        results = await repo.get_all()
        assert len(results) == len(sample_countries)
        assert set(c.country_code for c in results) == set(
            c.country_code for c in sample_countries
        )

    @pytest.mark.asyncio
    async def test_get_all_empty(self):
        """Should return empty list when no countries."""
        repo = InMemoryCountryRepository()
        results = await repo.get_all()
        assert results == []

    @pytest.mark.asyncio
    async def test_search_by_country_code(self, repo):
        """Should search countries by country code."""
        results, total = await repo.search("US", 10, 0)
        assert total == 1
        assert len(results) == 1
        assert results[0].country_code == "US"

    @pytest.mark.asyncio
    async def test_search_by_country_code_case_insensitive(self, repo):
        """Should search countries by country code case-insensitively."""
        results, total = await repo.search("us", 10, 0)
        assert total == 1
        assert len(results) == 1
        assert results[0].country_code == "US"

    @pytest.mark.asyncio
    async def test_search_by_country_name(self, repo):
        """Should search countries by country name."""
        results, total = await repo.search("United", 10, 0)
        assert total == 2  # United States, United Kingdom
        assert len(results) == 2
        assert "United" in results[0].country_name
        assert "United" in results[1].country_name

    @pytest.mark.asyncio
    async def test_search_by_country_name_case_insensitive(self, repo):
        """Should search countries by country name case-insensitively."""
        results, total = await repo.search("united", 10, 0)
        assert total == 2
        assert len(results) == 2

    @pytest.mark.asyncio
    async def test_search_by_timezone(self, repo):
        """Should search countries by timezone."""
        results, total = await repo.search("Asia", 10, 0)
        assert total == 1
        assert len(results) == 1
        assert results[0].country_code == "QA"
        assert results[0].timezone == "Asia/Qatar"

    @pytest.mark.asyncio
    async def test_search_by_timezone_case_insensitive(self, repo):
        """Should search countries by timezone case-insensitively."""
        results, total = await repo.search("asia", 10, 0)
        assert total == 1
        assert len(results) == 1
        assert results[0].country_code == "QA"

    @pytest.mark.asyncio
    async def test_search_no_results(self, repo):
        """Should return empty list when no matches found."""
        results, total = await repo.search("Nonexistent", 10, 0)
        assert total == 0
        assert len(results) == 0

    @pytest.mark.asyncio
    async def test_search_pagination_first_page(self, repo):
        """Should return first page of results."""
        results, total = await repo.search("t", 2, 0)  # 't' matches many countries
        assert total == 3  # US, GB, QA all have 't' in name
        assert len(results) == 2
        # Should be sorted by country_code: GB, QA, US
        assert results[0].country_code == "GB"
        assert results[1].country_code == "QA"

    @pytest.mark.asyncio
    async def test_search_pagination_second_page(self, repo):
        """Should return second page of results."""
        results, total = await repo.search("t", 2, 2)
        assert total == 3
        assert len(results) == 1
        # Third result should be: US
        assert results[0].country_code == "US"

    @pytest.mark.asyncio
    async def test_search_pagination_offset_beyond_results(self, repo):
        """Should return empty list when offset exceeds total."""
        results, total = await repo.search("t", 10, 10)
        assert total == 3
        assert len(results) == 0

    @pytest.mark.asyncio
    async def test_search_sort_order(self, repo):
        """Should return results sorted by country_code."""
        results, total = await repo.search("t", 10, 0)
        assert total == 3
        codes = [c.country_code for c in results]
        assert codes == sorted(codes)  # Check alphabetical order

    @pytest.mark.asyncio
    async def test_search_partial_match(self, repo):
        """Should return partial matches."""
        results, total = await repo.search("Unit", 10, 0)
        assert total == 2  # United States, United Kingdom
        assert len(results) == 2

    @pytest.mark.asyncio
    async def test_search_country_with_no_channels(self, repo):
        """Should include countries with no channels in search."""
        results, total = await repo.search("France", 10, 0)
        assert total == 1
        assert len(results) == 1
        assert results[0].country_code == "FR"
        assert results[0].has_channels is False
        assert results[0].channel_count == 0

    @pytest.mark.asyncio
    async def test_exist_true(self, repo, sample_countries):
        """Should return True when country exists."""
        country = sample_countries[0]
        result = await repo.exist(country.country_code)
        assert result is True

    @pytest.mark.asyncio
    async def test_exist_false(self, repo):
        """Should return False when country doesn't exist."""
        result = await repo.exist("XX")
        assert result is False

    @pytest.mark.asyncio
    async def test_exist_with_empty_string(self, repo):
        """Should return False for empty string."""
        result = await repo.exist("")
        assert result is False

    @pytest.mark.asyncio
    async def test_repository_with_empty_countries(self):
        """Should handle empty country list."""
        repo = InMemoryCountryRepository(countries=[])
        results = await repo.get_all()
        assert results == []

        result = await repo.get_by_id("US")
        assert result is None

        results, total = await repo.search("test", 10, 0)
        assert total == 0
        assert len(results) == 0

        exists = await repo.exist("US")
        assert exists is False

    @pytest.mark.asyncio
    async def test_country_with_special_characters(self):
        """Should handle countries with special characters."""
        countries = [
            Country(
                country_code="FR",
                country_name="France",
                timezone="Europe/Paris",
                has_channels=False,
                channel_count=0,
            ),
        ]
        repo = InMemoryCountryRepository(countries=countries)

        results, total = await repo.search("France", 10, 0)
        assert total == 1
        assert results[0].country_code == "FR"
