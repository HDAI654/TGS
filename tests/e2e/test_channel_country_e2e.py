# tests/e2e/test_graphql_e2e.py
import pytest
from httpx import AsyncClient, ASGITransport
from src.main import app
from src.core.database import engine, Base


class TestGraphQLCountryE2E:
    """End-to-end tests for GraphQL Country API."""

    @pytest.fixture(autouse=True)
    async def setup_db(self):
        """Setup and cleanup database for each test."""
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        yield
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    @pytest.fixture
    async def client(self):
        """Create HTTP client for testing."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            yield client

    # ========== HELPER METHODS ==========
    async def _graphql_request(
        self, client: AsyncClient, query: str, variables: dict = None
    ) -> dict:
        """Send GraphQL request and return response JSON."""
        payload = {"query": query}
        if variables:
            payload["variables"] = variables
        response = await client.post("/graphql/v1", json=payload)
        return response.json()

    # ========== COUNTRY LIFECYCLE TESTS ==========
    async def test_complete_country_lifecycle(self, client):
        """
        Complete country lifecycle:
        1. Create country
        2. Get country by code
        3. Search countries
        4. Update country
        5. Delete country
        """
        # ===== 1. Create country =====
        create_mutation = """
            mutation {
                createCountry(
                    countryCode: "FR"
                    countryName: "France"
                    capital: "Paris"
                    timezone: "Europe/Paris"
                    channelCount: 8
                ) {
                    countryCode
                    countryName
                    capital
                    timezone
                    channelCount
                }
            }
        """
        result = await self._graphql_request(client, create_mutation)
        assert "errors" not in result
        data = result["data"]["createCountry"]
        assert data["countryCode"] == "FR"
        assert data["countryName"] == "France"
        assert data["capital"] == "Paris"

        # ===== 2. Get country by code =====
        get_query = """
            query {
                country(countryCode: "FR") {
                    countryCode
                    countryName
                    capital
                    timezone
                    channelCount
                }
            }
        """
        result = await self._graphql_request(client, get_query)
        assert "errors" not in result
        data = result["data"]["country"]
        assert data["countryCode"] == "FR"
        assert data["countryName"] == "France"

        # ===== 3. Search countries =====
        search_query = """
            query {
                countries(filters: { country_code: "FR" }) {
                    countryCode
                    countryName
                    channelCount
                }
            }
        """
        result = await self._graphql_request(client, search_query)
        assert "errors" not in result
        countries = result["data"]["countries"]
        assert len(countries) == 1
        assert countries[0]["countryCode"] == "FR"

        # ===== 4. Update country =====
        update_mutation = """
            mutation {
                updateCountry(
                    countryCode: "FR"
                    newCountryName: "French Republic"
                    newChannelCount: 10
                )
            }
        """
        result = await self._graphql_request(client, update_mutation)
        assert "errors" not in result
        assert result["data"]["updateCountry"] is True

        # Verify update
        result = await self._graphql_request(client, get_query)
        data = result["data"]["country"]
        assert data["countryName"] == "French Republic"
        assert data["channelCount"] == 10

        # ===== 5. Delete country =====
        delete_mutation = """
            mutation {
                deleteCountry(countryCode: "FR")
            }
        """
        result = await self._graphql_request(client, delete_mutation)
        assert "errors" not in result
        assert result["data"]["deleteCountry"] is True

        # Verify deletion
        result = await self._graphql_request(client, get_query)
        assert "errors" in result
        assert result["errors"][0]["extensions"]["code"] == "COUNTRY_NOT_FOUND"

    # ========== CHANNEL LIFECYCLE TESTS ==========
    async def test_complete_channel_lifecycle(self, client):
        """
        Complete channel lifecycle:
        1. Create country (required for channel)
        2. Create channel
        3. Get channel by ID
        4. Search channels
        5. Add URL to channel
        6. Get channel URLs
        7. Update channel
        8. Delete channel
        """
        # ===== 1. Create country =====
        create_country = """
            mutation {
                createCountry(
                    countryCode: "UK"
                    countryName: "United Kingdom"
                    capital: "London"
                    timezone: "Europe/London"
                    channelCount: 5
                ) {
                    countryCode
                }
            }
        """
        result = await self._graphql_request(client, create_country)
        assert "errors" not in result

        # ===== 2. Create channel =====
        create_channel = """
            mutation {
                createChannel(
                    name: "BBC News"
                    category: "News"
                    language: "eng"
                    countryCode: "UK"
                    isGeoBlocked: false
                ) {
                    id
                    name
                    category
                    countryCode
                    isGeoBlocked
                }
            }
        """
        result = await self._graphql_request(client, create_channel)
        assert "errors" not in result
        data = result["data"]["createChannel"]
        channel_id = data["id"]
        assert data["name"] == "BBC News"
        assert data["countryCode"] == "UK"

        # ===== 3. Get channel by ID =====
        get_channel = """
            query GetChannel($id: String!) {
                channel(channelId: $id) {
                    id
                    name
                    category
                    countryCode
                    urls {
                        id
                        url
                    }
                }
            }
        """
        result = await self._graphql_request(client, get_channel, {"id": channel_id})
        assert "errors" not in result
        data = result["data"]["channel"]
        assert data["id"] == channel_id
        assert data["name"] == "BBC News"

        # ===== 4. Search channels =====
        search_channels = """
            query {
                channels(filters: { country_code: "UK" }) {
                    id
                    name
                    category
                    countryCode
                }
            }
        """
        result = await self._graphql_request(client, search_channels)
        assert "errors" not in result
        channels = result["data"]["channels"]
        assert len(channels) >= 1
        assert channels[0]["countryCode"] == "UK"

        # ===== 5. Add URL to channel =====
        add_url = """
            mutation AddUrl($id: String!) {
                addChannelUrl(channelId: $id, url: "https://www.bbc.com")
            }
        """
        result = await self._graphql_request(client, add_url, {"id": channel_id})
        assert "errors" not in result
        assert result["data"]["addChannelUrl"] is True

        # ===== 6. Get channel URLs =====
        get_urls = """
            query GetUrls($id: String!) {
                channelUrls(channelId: $id) {
                    url
                }
            }
        """
        result = await self._graphql_request(client, get_urls, {"id": channel_id})
        assert "errors" not in result
        urls = result["data"]["channelUrls"]
        assert len(urls) == 1
        assert urls[0]["url"] == "https://www.bbc.com"

        # ===== 7. Update channel =====
        update_channel = """
            mutation UpdateChannel($id: String!) {
                updateChannel(
                    channelId: $id
                    newName: "BBC World News"
                    newCategory: "International"
                )
            }
        """
        result = await self._graphql_request(client, update_channel, {"id": channel_id})
        assert "errors" not in result
        assert result["data"]["updateChannel"] is True

        # Verify update
        result = await self._graphql_request(client, get_channel, {"id": channel_id})
        data = result["data"]["channel"]
        assert data["name"] == "BBC World News"
        assert data["category"] == "International"

        # ===== 8. Delete channel =====
        delete_channel = """
            mutation DeleteChannel($id: String!) {
                deleteChannel(channelId: $id)
            }
        """
        result = await self._graphql_request(client, delete_channel, {"id": channel_id})
        assert "errors" not in result
        assert result["data"]["deleteChannel"] is True

        # Verify deletion
        result = await self._graphql_request(client, get_channel, {"id": channel_id})
        assert "errors" in result
        assert result["errors"][0]["extensions"]["code"] == "CHANNEL_NOT_FOUND"

    # ========== ERROR CASE TESTS ==========
    async def test_duplicate_country_error(self, client):
        """Creating a country with an existing code should return 409."""
        # Create first country
        create = """
            mutation {
                createCountry(
                    countryCode: "DE"
                    countryName: "Germany"
                    capital: "Berlin"
                    timezone: "Europe/Berlin"
                    channelCount: 10
                ) {
                    countryCode
                }
            }
        """
        result = await self._graphql_request(client, create)
        assert "errors" not in result

        # Try to create duplicate
        result = await self._graphql_request(client, create)
        assert "errors" in result
        assert result["errors"][0]["extensions"]["code"] == "DUPLICATE_COUNTRY"
        assert result["errors"][0]["extensions"]["status"] == 409

    async def test_country_not_found_error(self, client):
        """Getting non-existent country should return 404."""
        query = """
            query {
                country(countryCode: "XX") {
                    countryCode
                    countryName
                }
            }
        """
        result = await self._graphql_request(client, query)
        assert "errors" in result
        assert result["errors"][0]["extensions"]["code"] == "COUNTRY_NOT_FOUND"
        assert result["errors"][0]["extensions"]["status"] == 404

    async def test_no_changes_error(self, client):
        """Updating with no changes should return 400."""
        # Create country
        create = """
            mutation {
                createCountry(
                    countryCode: "ES"
                    countryName: "Spain"
                    capital: "Madrid"
                    timezone: "Europe/Madrid"
                    channelCount: 5
                ) {
                    countryCode
                }
            }
        """
        result = await self._graphql_request(client, create)
        assert "errors" not in result

        # Update with no changes
        update = """
            mutation {
                updateCountry(countryCode: "ES")
            }
        """
        result = await self._graphql_request(client, update)
        assert "errors" in result
        assert result["errors"][0]["extensions"]["code"] == "NO_CHANGES_ERROR"
        assert result["errors"][0]["extensions"]["status"] == 400

    async def test_channel_not_found_error(self, client):
        """Getting non-existent channel should return 404."""
        query = """
            query GetChannel($id: String!) {
                channel(channelId: $id) {
                    id
                    name
                }
            }
        """
        result = await self._graphql_request(client, query, {"id": "non-existent"})
        assert "errors" in result
        assert result["errors"][0]["extensions"]["code"] == "CHANNEL_NOT_FOUND"
        assert result["errors"][0]["extensions"]["status"] == 404
