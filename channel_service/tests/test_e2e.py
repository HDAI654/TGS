"""E2E tests for the GraphQL API running with in-memory repositories (development mode).

These tests do not require a real database. They use the seed data defined in
src/infrastructure/persistence/in_memory_seed.py.
"""

import os
from uuid import UUID

import pytest
from httpx import ASGITransport, AsyncClient

# Force development mode before importing app
os.environ["APP_ENV"] = "development"

from src.main import app
from src.infrastructure.persistence.in_memory.in_memory_seed import (
    channel_repo,
    country_repo,
)


@pytest.fixture
async def client():
    """Async client for testing."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


async def graphql_query(client: AsyncClient, query: str, variables: dict = None):
    """Helper to send a GraphQL query."""
    response = await client.post(
        "/graphql",
        json={"query": query, "variables": variables or {}},
    )
    return response.json()


@pytest.mark.asyncio
async def test_health_endpoint(client):
    """Health check should return healthy in development."""
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


@pytest.mark.asyncio
async def test_channel_by_id_found(client):
    """Retrieve an existing channel by its ID."""
    # Pick the first channel from the seed
    channel = next(iter(channel_repo._channels.values()))
    query = """
    query GetChannel($id: UUID!) {
        channel(id: $id) {
            id
            name
            category { id name }
            language
            countryCode
            urls
        }
    }
    """
    data = await graphql_query(client, query, {"id": str(channel.id)})
    assert "errors" not in data, f"GraphQL errors: {data.get('errors')}"
    result = data["data"]["channel"]
    assert result["id"] == str(channel.id)
    assert result["name"] == channel.name
    assert result["category"]["id"] == channel.category.id
    assert result["language"] == channel.language


@pytest.mark.asyncio
async def test_channel_by_id_not_found(client):
    """Return null for a non‑existent UUID."""
    fake_id = "00000000-0000-0000-0000-000000000000"
    query = """
    query GetChannel($id: UUID!) {
        channel(id: $id) { id name }
    }
    """
    data = await graphql_query(client, query, {"id": fake_id})
    assert "errors" not in data
    assert data["data"]["channel"] is None


@pytest.mark.asyncio
async def test_channels_pagination(client):
    """List channels with limit/offset, sorted by name then id."""
    # Note: channels query returns None when search is None or empty
    # So we need to use a non-empty search term
    query = """
    query GetChannels($limit: Int!, $offset: Int!, $search: String) {
        channels(limit: $limit, offset: $offset, search: $search) {
            items { id name }
            total
            limit
            offset
        }
    }
    """
    # Use a search term that matches all channels to get paginated results
    # The search term needs to be non-empty, but broad enough to match all
    data = await graphql_query(client, query, {"limit": 2, "offset": 0, "search": "e"})
    assert "errors" not in data, f"GraphQL errors: {data.get('errors')}"

    channels_data = data["data"]["channels"]
    assert channels_data is not None, "channels data should not be None"

    items = channels_data["items"]
    total = channels_data["total"]
    assert total == 4  # from seed: CNN, BBC, Al Jazeera, ESPN
    assert len(items) == 2
    # Sorted by name: Al Jazeera, BBC, CNN, ESPN
    assert items[0]["name"] == "Al Jazeera"
    assert items[1]["name"] == "BBC World"

    # Second page
    data2 = await graphql_query(client, query, {"limit": 2, "offset": 2, "search": "e"})
    assert "errors" not in data2, f"GraphQL errors: {data2.get('errors')}"
    channels_data2 = data2["data"]["channels"]
    assert channels_data2 is not None
    items2 = channels_data2["items"]
    assert len(items2) == 2
    assert items2[0]["name"] == "CNN"
    assert items2[1]["name"] == "ESPN"


@pytest.mark.asyncio
async def test_channels_search(client):
    """Search channels by name, category, country, or language."""
    query = """
    query SearchChannels($search: String!, $limit: Int!, $offset: Int!) {
        channels(search: $search, limit: $limit, offset: $offset) {
            items { name }
            total
        }
    }
    """
    # By name
    data = await graphql_query(
        client, query, {"search": "CNN", "limit": 10, "offset": 0}
    )
    assert "errors" not in data
    assert data["data"]["channels"]["total"] == 1
    assert data["data"]["channels"]["items"][0]["name"] == "CNN"

    # By category name
    data = await graphql_query(
        client, query, {"search": "News", "limit": 10, "offset": 0}
    )
    assert "errors" not in data
    # CNN, BBC, Al Jazeera are all "News"
    assert data["data"]["channels"]["total"] == 3

    # By country name (via in-memory country_name_map)
    data = await graphql_query(
        client, query, {"search": "United", "limit": 10, "offset": 0}
    )
    assert "errors" not in data
    # United States -> CNN, ESPN; United Kingdom -> BBC
    assert data["data"]["channels"]["total"] == 3

    # By language
    data = await graphql_query(
        client, query, {"search": "ar", "limit": 10, "offset": 0}
    )
    assert "errors" not in data
    assert data["data"]["channels"]["total"] == 1
    assert data["data"]["channels"]["items"][0]["name"] == "Al Jazeera"


@pytest.mark.asyncio
async def test_country_by_code_found(client):
    """Retrieve an existing country by its code."""
    query = """
    query GetCountry($code: String!) {
        country(countryCode: $code) {
            countryCode
            countryName
            timezone
            hasChannels
            channelCount
        }
    }
    """
    data = await graphql_query(client, query, {"code": "US"})
    assert "errors" not in data, f"GraphQL errors: {data.get('errors')}"
    country = data["data"]["country"]
    assert country["countryCode"] == "US"
    assert country["countryName"] == "United States"
    assert country["timezone"] == "America/New_York"
    assert country["hasChannels"] is True
    assert country["channelCount"] == 3


@pytest.mark.asyncio
async def test_country_by_code_not_found(client):
    """Return null for a non‑existent country code."""
    query = """
    query GetCountry($code: String!) {
        country(countryCode: $code) { countryCode }
    }
    """
    data = await graphql_query(client, query, {"code": "XX"})
    assert "errors" not in data
    assert data["data"]["country"] is None


@pytest.mark.asyncio
async def test_countries_pagination(client):
    """List countries with pagination, sorted by countryCode."""
    query = """
    query GetCountries($limit: Int!, $offset: Int!, $search: String) {
        countries(limit: $limit, offset: $offset, search: $search) {
            items { countryCode }
            total
        }
    }
    """
    data = await graphql_query(client, query, {"limit": 2, "offset": 0, "search": "t"})
    assert "errors" not in data, f"GraphQL errors: {data.get('errors')}"

    countries_data = data["data"]["countries"]
    assert countries_data is not None, "countries data should not be None"

    items = countries_data["items"]
    total = countries_data["total"]
    assert total == 3  # GB, QA, US - all have 't' in their names
    assert len(items) == 2
    # Sorted by code: GB, QA, US
    assert items[0]["countryCode"] == "GB"
    assert items[1]["countryCode"] == "QA"


@pytest.mark.asyncio
async def test_countries_search(client):
    """Search countries by code, name, or timezone."""
    query = """
    query SearchCountries($search: String!, $limit: Int!, $offset: Int!) {
        countries(search: $search, limit: $limit, offset: $offset) {
            items { countryCode countryName }
            total
        }
    }
    """
    # By code
    data = await graphql_query(
        client, query, {"search": "GB", "limit": 10, "offset": 0}
    )
    assert "errors" not in data
    assert data["data"]["countries"]["total"] == 1
    assert data["data"]["countries"]["items"][0]["countryCode"] == "GB"

    # By name
    data = await graphql_query(
        client, query, {"search": "United", "limit": 10, "offset": 0}
    )
    assert "errors" not in data
    assert data["data"]["countries"]["total"] == 2  # United States, United Kingdom

    # By timezone
    data = await graphql_query(
        client, query, {"search": "Asia", "limit": 10, "offset": 0}
    )
    assert "errors" not in data
    assert data["data"]["countries"]["total"] == 1
    assert data["data"]["countries"]["items"][0]["countryCode"] == "QA"
