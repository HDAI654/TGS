import pytest
import json
import zlib
from unittest.mock import AsyncMock, patch
from httpx import Response
from workers.imp.tv_garden_crawler_imp import TVGardenCrawlerImp
from workers.core.exceptions import (
    CrawlerConnectionError,
    CrawlerHTTPError,
)
from shared.domain.entities.country import CountryEntity
from shared.domain.entities.channel import ChannelEntity


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
                "nanoid": "abc123",
                "name": "CNN",
                "languages": ["eng"],
                "country": "US",
                "isGeoBlocked": False,
                "stream_urls": ["https://stream.cnn.com"],
                "youtube_urls": ["https://youtube.com/cnn"],
            },
            {
                "nanoid": "def456",
                "name": "BBC",
                "languages": ["eng"],
                "country": "UK",
                "isGeoBlocked": False,
                "stream_urls": ["https://stream.bbc.com"],
                "youtube_urls": [],
            },
        ]

    def _compress_data(self, data: dict) -> bytes:
        """Compress with proper zlib format."""
        return zlib.compress(json.dumps(data).encode("utf-8"))

    def _create_mock_response(self, content: bytes, status: int = 200):
        mock = AsyncMock(spec=Response)
        mock.status_code = status
        mock.content = content
        try:
            mock.json.return_value = json.loads(content.decode("utf-8"))
        except:
            mock.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        return mock

    # ========== EXTRACT ALL COUNTRIES ==========
    async def test_extract_all_countries_success(self, crawler, mock_countries_data):
        compressed = self._compress_data(mock_countries_data)
        mock_response = self._create_mock_response(compressed)

        with patch.object(crawler, "_fetch_url", AsyncMock(return_value=mock_response)):
            with patch.object(
                crawler, "_decompressor", return_value=mock_countries_data
            ):
                result = await crawler.extract_all_countries()

        assert len(result) == 2
        assert isinstance(result[0], CountryEntity)
        assert result[0].country_code.value == "US"
        assert result[1].country_code.value == "FR"

    async def test_extract_all_countries_empty(self, crawler):
        with patch.object(crawler, "_fetch_url", AsyncMock(return_value=None)):
            with patch.object(crawler, "_decompressor", return_value={}):
                result = await crawler.extract_all_countries()
        assert result == []

    async def test_extract_all_countries_connection_error(self, crawler):
        with patch.object(
            crawler, "_fetch_url", side_effect=CrawlerConnectionError("Failed")
        ):
            with pytest.raises(CrawlerConnectionError):
                await crawler.extract_all_countries()

    async def test_extract_all_countries_http_error(self, crawler):
        with patch.object(crawler, "_fetch_url", side_effect=CrawlerHTTPError("404")):
            with pytest.raises(CrawlerHTTPError):
                await crawler.extract_all_countries()

    # ========== EXTRACT ALL CHANNELS ==========
    async def test_extract_all_channels_success(self, crawler, mock_channels_data):
        compressed = self._compress_data(mock_channels_data)
        mock_response = self._create_mock_response(compressed)

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

    async def test_extract_all_channels_handles_failed_category(
        self, crawler, mock_channels_data
    ):
        def mock_fetch_side_effect(url):
            if "news" in url:
                raise CrawlerHTTPError("404")
            return self._create_mock_response(self._compress_data(mock_channels_data))

        with patch.object(crawler, "_fetch_url", side_effect=mock_fetch_side_effect):
            with patch.object(
                crawler, "_decompressor", return_value=mock_channels_data
            ):
                result = await crawler.extract_all_channels()
                assert isinstance(result, dict)

    async def test_extract_all_channels_empty_response(self, crawler):
        with patch.object(crawler, "_fetch_url", AsyncMock(return_value=None)):
            with patch.object(crawler, "_decompressor", return_value=[]):
                result = await crawler.extract_all_channels()
                assert result == {}
