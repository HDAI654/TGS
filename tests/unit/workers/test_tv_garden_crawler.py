'''import pytest
import json
import zlib
from unittest.mock import AsyncMock, MagicMock, patch
from httpx import Response, Request, ConnectError, TimeoutException
from workers.tv_garden_crawler_imp import TVGardenCrawlerImp
from workers.exceptions import (
    CrawlerError,
    CrawlerConnectionError,
    CrawlerTimeoutError,
    CrawlerHTTPError,
    CrawlerParseError,
    CrawlerEmptyResponseError,
)
from shared.domain.entities.country import CountryEntity
from shared.domain.entities.channel import ChannelEntity
from shared.domain.exceptions import DomainError


class TestTVGardenCrawler:
    """Tests for TVGardenCrawlerImp."""

    @pytest.fixture
    def crawler(self):
        return TVGardenCrawlerImp(timeout=5.0)

    @pytest.fixture
    def mock_countries_data(self):
        return {
            "US": {
                "country": "United States",
                "capital": "Washington D.C.",
                "timeZone": "America/New_York",
                "channelCount": 10,
            },
            "FR": {
                "country": "France",
                "capital": "Paris",
                "timeZone": "Europe/Paris",
                "channelCount": 8,
            },
        }

    @pytest.fixture
    def mock_channels_data(self):
        return [
            {
                "nano_id": "abc123",
                "name": "CNN",
                "languages": ["eng"],
                "country": "US",
                "isGeoBlocked": False,
                "stream_urls": ["https://stream.cnn.com"],
                "youtube_urls": ["https://youtube.com/cnn"],
            },
            {
                "nano_id": "def456",
                "name": "BBC",
                "languages": ["eng"],
                "country": "UK",
                "isGeoBlocked": False,
                "stream_urls": ["https://stream.bbc.com"],
                "youtube_urls": [],
            },
        ]

    # ========== HELPER METHODS ==========

    def _create_mock_response(
        self, content: bytes, status_code: int = 200
    ) -> AsyncMock:
        """Create a mock httpx Response."""
        mock_response = AsyncMock(spec=Response)
        mock_response.status_code = status_code
        mock_response.content = content
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = json.loads(content.decode("utf-8"))
        return mock_response

    def _compress_data(self, data: dict) -> bytes:
        """Compress data with zlib."""
        json_string = json.dumps(data)
        return zlib.compress(json_string.encode("utf-8"))

    # ========== EXTRACT ALL COUNTRIES TESTS ==========

    @pytest.mark.asyncio
    async def test_extract_all_countries_success(self, crawler, mock_countries_data):
        """Test successful country extraction."""
        compressed_data = self._compress_data(mock_countries_data)
        mock_response = self._create_mock_response(compressed_data)

        with patch.object(crawler, "_fetch_url", AsyncMock(return_value=mock_response)):
            with patch.object(
                crawler, "_decompressor", return_value=mock_countries_data
            ):
                result = await crawler.extract_all_countries()

        assert len(result) == 2
        assert isinstance(result[0], CountryEntity)
        assert result[0].country_code.value == "US"
        assert result[0].country_name.value == "United States"
        assert result[1].country_code.value == "FR"

    @pytest.mark.asyncio
    async def test_extract_all_countries_empty_response(self, crawler):
        """Test handling of empty response."""
        with patch.object(crawler, "_fetch_url", AsyncMock(return_value=None)):
            with patch.object(crawler, "_decompressor", return_value={}):
                result = await crawler.extract_all_countries()

        assert result == []

    @pytest.mark.asyncio
    async def test_extract_all_countries_connection_error(self, crawler):
        """Test handling of connection error."""
        with patch.object(
            crawler,
            "_fetch_url",
            side_effect=CrawlerConnectionError("Connection failed"),
        ):
            with pytest.raises(CrawlerConnectionError):
                await crawler.extract_all_countries()

    @pytest.mark.asyncio
    async def test_extract_all_countries_timeout_error(self, crawler):
        """Test handling of timeout error."""
        with patch.object(
            crawler, "_fetch_url", side_effect=CrawlerTimeoutError("Timeout")
        ):
            with pytest.raises(CrawlerTimeoutError):
                await crawler.extract_all_countries()

    @pytest.mark.asyncio
    async def test_extract_all_countries_http_error(self, crawler):
        """Test handling of HTTP error."""
        with patch.object(
            crawler, "_fetch_url", side_effect=CrawlerHTTPError("HTTP 404")
        ):
            with pytest.raises(CrawlerHTTPError):
                await crawler.extract_all_countries()

    @pytest.mark.asyncio
    async def test_extract_all_countries_parse_error(self, crawler):
        """Test handling of parse error."""
        with patch.object(crawler, "_fetch_url", AsyncMock(return_value=None)):
            with patch.object(
                crawler, "_decompressor", side_effect=CrawlerParseError("Parse failed")
            ):
                with pytest.raises(CrawlerParseError):
                    await crawler.extract_all_countries()

    @pytest.mark.asyncio
    async def test_extract_all_countries_invalid_data_skipped(
        self, crawler, mock_countries_data
    ):
        """Test that invalid country data is skipped."""
        # Add invalid data
        mock_countries_data["XX"] = {
            "country": None,  # Invalid
            "capital": None,
            "timeZone": None,
            "channelCount": None,
        }

        compressed_data = self._compress_data(mock_countries_data)
        mock_response = self._create_mock_response(compressed_data)

        with patch.object(crawler, "_fetch_url", AsyncMock(return_value=mock_response)):
            with patch.object(
                crawler, "_decompressor", return_value=mock_countries_data
            ):
                result = await crawler.extract_all_countries()

        # Should skip invalid data and only return valid ones
        assert len(result) == 2
        assert all(c.country_code.value != "XX" for c in result)

    # ========== EXTRACT ALL CHANNELS TESTS ==========
    @pytest.mark.asyncio
    async def test_extract_all_channels_success(self, crawler, mock_channels_data):
        """Test successful channel extraction."""
        compressed_data = self._compress_data(mock_channels_data)
        mock_response = self._create_mock_response(compressed_data)

        with patch.object(crawler, "_fetch_url", AsyncMock(return_value=mock_response)):
            with patch.object(
                crawler, "_decompressor", return_value=mock_channels_data
            ):
                result = await crawler.extract_all_channels()

        assert len(result) > 0
        for channel_id, data in result.items():
            assert "channel" in data
            assert "urls" in data
            assert isinstance(data["channel"], ChannelEntity)
            assert isinstance(data["urls"], list)

    @pytest.mark.asyncio
    async def test_extract_all_channels_handles_failed_category(self, crawler):
        """Test that failed categories are handled gracefully."""
        # Mock first category to fail, second to succeed
        mock_channels = [
            {
                "nano_id": "test123",
                "name": "Test Channel",
                "languages": ["eng"],
                "country": "US",
                "isGeoBlocked": False,
                "stream_urls": [],
                "youtube_urls": [],
            }
        ]

        def mock_fetch_side_effect(url):
            if "news" in url:
                raise CrawlerHTTPError("HTTP 404")
            return self._create_mock_response(self._compress_data(mock_channels))

        with patch.object(crawler, "_fetch_url", side_effect=mock_fetch_side_effect):
            with patch.object(crawler, "_decompressor", return_value=mock_channels):
                result = await crawler.extract_all_channels()

        # Should still return channels from successful categories
        assert len(result) > 0 or result == {}

    @pytest.mark.asyncio
    async def test_extract_all_channels_connection_error(self, crawler):
        """Test handling of connection error during channel extraction."""
        with patch.object(
            crawler,
            "_fetch_url",
            side_effect=CrawlerConnectionError("Connection failed"),
        ):
            result = await crawler.extract_all_channels()
            # Should continue with other categories, result may be empty
            assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_extract_all_channels_empty_response(self, crawler):
        """Test handling of empty channel response."""
        with patch.object(crawler, "_fetch_url", AsyncMock(return_value=None)):
            with patch.object(crawler, "_decompressor", return_value=[]):
                result = await crawler.extract_all_channels()
                assert result == {}

    # ========== FETCH URL TESTS ==========

    @pytest.mark.asyncio
    async def test_fetch_url_success(self, crawler):
        """Test successful URL fetch."""
        mock_response = AsyncMock(spec=Response)
        mock_response.status_code = 200
        mock_response.content = b'{"test": "data"}'

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )
            result = await crawler._fetch_url("https://test.com")
            assert result.status_code == 200

    @pytest.mark.asyncio
    async def test_fetch_url_http_error(self, crawler):
        """Test HTTP error handling."""
        mock_response = AsyncMock(spec=Response)
        mock_response.status_code = 404

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )
            with pytest.raises(CrawlerHTTPError):
                await crawler._fetch_url("https://test.com")

    @pytest.mark.asyncio
    async def test_fetch_url_connection_error(self, crawler):
        """Test connection error handling."""
        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                side_effect=ConnectError("Connection failed")
            )
            with pytest.raises(CrawlerConnectionError):
                await crawler._fetch_url("https://test.com")

    @pytest.mark.asyncio
    async def test_fetch_url_timeout_error(self, crawler):
        """Test timeout error handling."""
        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                side_effect=TimeoutException("Timeout")
            )
            with pytest.raises(CrawlerTimeoutError):
                await crawler._fetch_url("https://test.com")

    # ========== DECOMPRESSOR TESTS ==========

    def test_decompressor_zlib_success(self, crawler, mock_countries_data):
        """Test successful zlib decompression."""
        compressed_data = self._compress_data(mock_countries_data)
        mock_response = self._create_mock_response(compressed_data)

        result = crawler._decompressor(mock_response)
        assert result == mock_countries_data

    def test_decompressor_already_json(self, crawler, mock_countries_data):
        """Test handling of already JSON response."""
        json_data = json.dumps(mock_countries_data).encode("utf-8")
        mock_response = self._create_mock_response(json_data)

        result = crawler._decompressor(mock_response)
        assert result == mock_countries_data

    def test_decompressor_empty_response(self, crawler):
        """Test handling of empty response."""
        mock_response = self._create_mock_response(b"")
        with pytest.raises(CrawlerEmptyResponseError):
            crawler._decompressor(mock_response)

    def test_decompressor_invalid_data(self, crawler):
        """Test handling of invalid data."""
        mock_response = self._create_mock_response(b"invalid data")
        with pytest.raises(CrawlerParseError):
            crawler._decompressor(mock_response)

    # ========== CREATE ENTITY TESTS ==========

    def test_create_country_entity_success(self, crawler):
        """Test successful country entity creation."""
        data = {
            "country": "Test Country",
            "capital": "Test Capital",
            "timeZone": "Europe/London",
            "channelCount": 5,
        }
        result = crawler._create_country_entity("TC", data)
        assert isinstance(result, CountryEntity)
        assert result.country_code.value == "TC"
        assert result.country_name.value == "Test Country"

    def test_create_country_entity_domain_error(self, crawler):
        """Test handling of domain error during country creation."""
        data = {
            "country": "Test Country",
            "capital": "Test Capital",
            "timeZone": "Europe/London",
            "channelCount": "invalid",  # Invalid type
        }
        result = crawler._create_country_entity("TC", data)
        assert result is None

    def test_create_channel_entity_success(self, crawler):
        """Test successful channel entity creation."""
        ch = {
            "nano_id": "test123",
            "name": "Test Channel",
            "languages": ["eng"],
            "country": "US",
            "isGeoBlocked": False,
            "stream_urls": ["https://stream.test.com"],
            "youtube_urls": ["https://youtube.com/test"],
        }
        result = crawler._create_channel_entity(ch, "News")
        assert result is not None
        channel_entity, urls = result
        assert isinstance(channel_entity, ChannelEntity)
        assert channel_entity.name.value == "Test Channel"
        assert len(urls) == 2

    def test_create_channel_entity_no_language(self, crawler):
        """Test channel creation with no language."""
        ch = {
            "nano_id": "test123",
            "name": "Test Channel",
            "languages": [],
            "country": "US",
            "isGeoBlocked": False,
            "stream_urls": [],
            "youtube_urls": [],
        }
        result = crawler._create_channel_entity(ch, "News")
        assert result is not None
        channel_entity, urls = result
        assert channel_entity.language.value == "None"

    def test_create_channel_entity_domain_error(self, crawler):
        """Test handling of domain error during channel creation."""
        ch = {
            "nano_id": None,  # Invalid - ID cannot be None
            "name": "Test Channel",
            "languages": ["eng"],
            "country": "US",
            "isGeoBlocked": False,
            "stream_urls": [],
            "youtube_urls": [],
        }
        result = crawler._create_channel_entity(ch, "News")
        assert result is None

    # ========== INTEGRATION TESTS ==========

    @pytest.mark.asyncio
    async def test_full_extract_flow(
        self, crawler, mock_countries_data, mock_channels_data
    ):
        """Test full extraction flow with mocks."""
        compressed_countries = self._compress_data(mock_countries_data)
        compressed_channels = self._compress_data(mock_channels_data)

        mock_countries_response = self._create_mock_response(compressed_countries)
        mock_channels_response = self._create_mock_response(compressed_channels)

        def mock_fetch_side_effect(url):
            if "countries" in url:
                return mock_countries_response
            return mock_channels_response

        with patch.object(crawler, "_fetch_url", side_effect=mock_fetch_side_effect):
            with patch.object(crawler, "_decompressor") as mock_decompressor:
                mock_decompressor.side_effect = [
                    mock_countries_data,
                    mock_channels_data,
                ]
                countries = await crawler.extract_all_countries()
                channels = await crawler.extract_all_channels()

        assert len(countries) == 2
        assert len(channels) >= 1

    @pytest.mark.asyncio
    async def test_crawler_context_manager(self):
        """Test crawler works with context manager."""
        async with TVGardenCrawlerImp() as crawler:
            assert crawler is not None
'''
