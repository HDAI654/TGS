import logging
import httpx
import zlib
import json
import random
from workers.crawler_interface import ICrawler
from shared.domain.entities.channel import ChannelEntity
from shared.domain.entities.country import CountryEntity
from shared.domain.entities.url_entity import URLEntity
from shared.domain.factories.channel_factory import ChannelFactory
from shared.domain.factories.country_factory import CountryFactory
from shared.domain.factories.url_factory import URLFactory
from shared.domain.exceptions import DomainError
from shared.domain.id_vo import ID
from workers.exceptions import (
    CrawlerError,
    CrawlerConnectionError,
    CrawlerTimeoutError,
    CrawlerHTTPError,
    CrawlerParseError,
    CrawlerEmptyResponseError,
)

logger = logging.getLogger(__name__)


class TVGardenCrawlerImp(ICrawler):
    """Implementation Crawler using tv-garden data."""

    # URLs
    COUNTRIES_URL = "https://tvgarden.world/api/tv/countries_metadata.json"
    CATEGORIES_URL = "https://tvgarden.world/api/tv/categories/{category}.json"

    # Request settings
    TIMEOUT = 30.0
    MAX_RETRIES = 3
    RETRY_WAIT_MIN = 1
    RETRY_WAIT_MAX = 10

    AVAILABLE_CATEGORIES = {
        "Top News": "top-news",
        "News": "news",
        "Music": "music",
        "Sports": "sports",
        "Auto": "auto",
        "Animation": "animation",
        "Business": "business",
        "Classic": "classic",
        "Comedy": "comedy",
        "Cooking": "cooking",
        "Culture": "culture",
        "Documentary": "documentary",
        "Education": "education",
        "Entertainment": "entertainment",
        "Family": "family",
        "General": "general",
        "Kids": "kids",
        "Legislative": "legislative",
        "Lifestyle": "lifestyle",
        "Movies": "movies",
        "Outdoor": "outdoor",
        "Relax": "relax",
        "Religious": "religious",
        "Series": "series",
        "Science": "science",
        "Shop": "shop",
        "Travel": "travel",
        "Weather": "weather",
    }

    def __init__(self, timeout: float = TIMEOUT):
        self.timeout = timeout

    def _decompressor(self, response: httpx.Response) -> dict:
        """Decompress zlib/gzip response or parse JSON."""
        logger.debug("Decompressing response's content")
        content = response.content

        if not content:
            raise CrawlerEmptyResponseError("Response content is empty")

        # Try zlib decompression
        try:
            decompressed_data = zlib.decompress(content, 16 + zlib.MAX_WBITS)
            json_string = decompressed_data.decode("utf-8")
            data = json.loads(json_string)
            logger.debug("Response decompressed successfully")
            return data

        except zlib.error as e:
            logger.debug(f"Decompression failed, trying JSON: {e}")
            try:
                data = response.json()
                logger.debug("Response is already JSON")
                return data
            except Exception as e2:
                logger.exception("Could not parse response")
                raise CrawlerParseError("Could not parse response:")

    async def _fetch_url(self, url: str) -> httpx.Response:
        """Fetch URL with timeout and error handling."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url)

                if response.status_code != 200:
                    logger.error("HTTP %s from %s", response.status_code, url)
                    raise CrawlerHTTPError(f"HTTP {response.status_code} from {url}")

                return response

        except httpx.ConnectError as e:
            logger.exception("Failed to connect to %s", url)
            raise CrawlerConnectionError(f"Failed to connect to {url}")
        except httpx.TimeoutException as e:
            logger.exception("Request to %s timed out after %ss", url, self.timeout)
            raise CrawlerTimeoutError(
                f"Request to {url} timed out after {self.timeout}s"
            )

    def _create_country_entity(self, code: str, data: dict) -> CountryEntity | None:
        """Create a CountryEntity from raw data."""
        try:
            return CountryFactory.create(
                country_code=str(code),
                country_name=str(data.get("country")),
                capital=str(data.get("capital")),
                timezone=str(data.get("timeZone")),
                channel_count=int(data.get("channelCount")),
            )
        except DomainError as e:
            logger.warning(
                "Creating country-entity failed: country_code=%s, error=%s",
                str(code),
                str(e),
            )
            return None

    def _create_channel_entity(
        self, ch: dict, category_name: str
    ) -> tuple[ChannelEntity, list[URLEntity]] | None:
        """Create a ChannelEntity and its URLs from raw data."""
        try:
            # Handle short IDs
            id = str(ch.get("nanoid"))
            chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
            if id and len(id) < ID.STANDARD_ID_LENGTH:
                id = id + "".join(
                    random.choices(chars, k=ID.STANDARD_ID_LENGTH - len(id))
                )

            # Get language (handle missing or empty)
            languages = ch.get("languages", [])
            language = languages[0] if languages else "ukn"  # ukn = unknown

            channel_entity = ChannelFactory.create(
                id=id,
                name=str(ch.get("name")),
                category=category_name,
                language=str(language),
                country_code=ch.get("country"),
                is_geo_blocked=bool(ch.get("isGeoBlocked")),
            )

            # Create URLs
            stream_urls = ch.get("stream_urls", [])
            youtube_urls = ch.get("youtube_urls", [])
            all_urls = list(stream_urls) + list(youtube_urls)

            url_entities = [
                URLFactory.create(url=url)
                for url in all_urls
                if url and isinstance(url, str)
            ]

            return channel_entity, url_entities

        except DomainError as e:
            logger.warning(
                "Creating channel-entity failed: channel_id=%s, error=%s",
                ch.get("nanoid", "unknown"),
                str(e),
            )
            print(ch)
            print("*" * 10)
            print("*" * 10)
            print("*" * 10)
            print("*" * 10)
            return None

    # ========== MAIN METHODS ==========
    async def extract_all_countries(self) -> list[CountryEntity]:
        """Extract all countries from the API."""
        logger.info("Extracting countries data: URL=%s", self.COUNTRIES_URL)

        try:
            response = await self._fetch_url(self.COUNTRIES_URL)
            data = self._decompressor(response)

            if not data:
                logger.warning("No country data received")
                return []

            logger.info(f"Received data for {len(data)} countries")

            countries = []
            for code, country_data in data.items():
                country = self._create_country_entity(code, country_data)
                if country:
                    countries.append(country)

            logger.info(
                "Countries data extracted successfully: %d countries", len(countries)
            )
            return countries

        except CrawlerError:
            logger.error("Extracting countries data failed")
            raise

    async def extract_all_channels(self) -> dict[str, dict]:
        """Extract all channels from the API."""
        logger.info(
            "Extracting channels data from %d categories",
            len(self.AVAILABLE_CATEGORIES),
        )

        channels_data = {}
        failed_categories = []
        total_channels = 0

        for category_name, category_code in self.AVAILABLE_CATEGORIES.items():
            try:
                url = self.CATEGORIES_URL.format(category=category_code)
                logger.debug("Fetching category: %s (%s)", category_name, category_code)

                response = await self._fetch_url(url)
                data = self._decompressor(response)

                if not data:
                    logger.warning("No data for category: %s", category_name)
                    failed_categories.append(category_name)
                    continue

                count = 0
                for ch in data:
                    result = self._create_channel_entity(ch, category_name)
                    if result:
                        channel_entity, url_entities = result
                        channels_data[channel_entity.id.value] = {
                            "channel": channel_entity,
                            "urls": url_entities,
                        }
                        count += 1

                total_channels += count
                logger.info(
                    "Extracted %d channels from category '%s'", count, category_name
                )

            except CrawlerHTTPError:
                failed_categories.append(category_name)
                continue
            except Exception as e:
                logger.exception("Error extracting category '%s'", category_name)
                failed_categories.append(category_name)
                continue

        logger.info(
            "Channels data extracted successfully: %d channels from %d/%d categories",
            total_channels,
            len(self.AVAILABLE_CATEGORIES) - len(failed_categories),
            len(self.AVAILABLE_CATEGORIES),
        )

        if failed_categories:
            logger.warning("Failed categories: %s", failed_categories)

        return channels_data
