import gzip
import json
import logging
import uuid
import zlib
from collections.abc import Iterable
from typing import Any
import httpx
from celery import shared_task
from django.db import transaction
from src.apps.categories.models import Category
from src.apps.channels.models import Channel
from src.apps.countries.models import Country

logger = logging.getLogger(__name__)


class TVGardenCrawler:
    """Fetch and normalize data from the TV Garden API."""

    COUNTRIES_URL = "https://tvgarden.world/api/tv/countries_metadata.json"
    CATEGORIES_URL = "https://tvgarden.world/api/tv/categories/{category}.json"

    TIMEOUT = 30.0

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

    def __init__(self, timeout: float = TIMEOUT) -> None:
        self.timeout = timeout

    def fetch_json(self, url: str) -> dict:
        response = httpx.get(
            url,
            timeout=30.0,
            headers={
                "Accept": "application/json",
                "Accept-Encoding": "gzip, deflate",
            },
        )
        response.raise_for_status()

        content = response.content

        if content.startswith(b"\x1f\x8b"):
            content = gzip.decompress(content)
        elif content.startswith((b"\x78\x01", b"\x78\x9c", b"\x78\xda")):
            content = zlib.decompress(content)

        return json.loads(content.decode("utf-8"))

    @staticmethod
    def _decompress_content(content: bytes) -> bytes:
        """Decompress gzip or zlib content."""
        decompressors = (
            lambda value: gzip.decompress(value),
            lambda value: zlib.decompress(value),
            lambda value: zlib.decompress(
                value,
                16 + zlib.MAX_WBITS,
            ),
        )

        for decompressor in decompressors:
            try:
                return decompressor(content)
            except zlib.error:
                continue
            except OSError:
                continue

        return content

    def extract_countries(self) -> list[dict[str, Any]]:
        """Extract country records from TV Garden."""
        data = self.fetch_json(self.COUNTRIES_URL)

        if not isinstance(data, dict):
            raise ValueError("Countries API returned an unexpected format")

        countries: list[dict[str, Any]] = []

        for country_code, country_data in data.items():
            if not isinstance(country_data, dict):
                logger.warning(
                    "Skipping invalid country data: %s",
                    country_code,
                )
                continue

            countries.append(
                {
                    "country_code": str(country_code).upper(),
                    "country_name": str(country_data.get("country") or country_code),
                    "timezone": str(country_data.get("timeZone") or "UTC"),
                    "channel_count": self._to_int(country_data.get("channelCount")),
                }
            )

        return countries

    def extract_channels(self) -> list[dict[str, Any]]:
        """Extract channel records from all TV Garden categories."""
        channels: list[dict[str, Any]] = []

        for category_name, category_code in self.AVAILABLE_CATEGORIES.items():
            url = self.CATEGORIES_URL.format(category=category_code)

            try:
                data = self.fetch_json(url)
            except httpx.HTTPError:
                logger.exception(
                    "HTTP error while fetching category '%s'",
                    category_name,
                )
                continue
            except ValueError:
                logger.exception(
                    "Invalid response while fetching category '%s'",
                    category_name,
                )
                continue

            if not isinstance(data, list):
                logger.warning(
                    "Skipping category '%s': expected a list",
                    category_name,
                )
                continue

            for raw_channel in data:
                if not isinstance(raw_channel, dict):
                    continue

                channel = self._normalize_channel(
                    raw_channel,
                    category_name,
                )

                if channel is not None:
                    channels.append(channel)

        return channels

    @staticmethod
    def _normalize_channel(
        raw_channel: dict[str, Any],
        category_name: str,
    ) -> dict[str, Any] | None:
        """Convert one raw TV Garden channel into a Django-ready record."""
        name = raw_channel.get("name")
        country_code = raw_channel.get("country")

        if not name or not country_code:
            logger.warning(
                "Skipping channel without name or country: %s",
                raw_channel,
            )
            return None

        languages = raw_channel.get("languages") or []
        language = (
            str(languages[0])
            if isinstance(languages, list) and languages
            else "unknown"
        )

        stream_urls = raw_channel.get("stream_urls") or []
        youtube_urls = raw_channel.get("youtube_urls") or []

        urls = [
            str(url)
            for url in [*stream_urls, *youtube_urls]
            if isinstance(url, str) and url.strip()
        ]

        return {
            "name": str(name).strip(),
            "category": category_name,
            "language": language,
            "country_code": str(country_code).upper(),
            "urls": {"urls": urls},
        }

    @staticmethod
    def _to_int(value: Any) -> int:
        """Safely convert a value to a non-negative integer."""
        try:
            return max(0, int(value or 0))
        except (TypeError, ValueError):
            return 0


def _update_countries(
    country_records: Iterable[dict[str, Any]],
) -> int:
    """Upsert countries and return the number of processed records."""
    processed = 0

    for record in country_records:
        country_code = record["country_code"]

        Country.objects.update_or_create(
            country_code=country_code,
            defaults={
                "country_name": record["country_name"],
                "timezone": record["timezone"],
                "channel_count": record["channel_count"],
                "has_channels": record["channel_count"] > 0,
            },
        )

        processed += 1

    return processed


def _update_channels(
    channel_records: Iterable[dict[str, Any]],
) -> int:
    """
    Upsert channels and return the number of processed records.

    Since the current Channel model has no external TV Garden identifier,
    channels are matched by name, category, and country.
    """
    processed = 0

    for record in channel_records:
        category, _ = Category.objects.get_or_create(
            name=record["category"],
        )

        country = Country.objects.filter(
            country_code=record["country_code"],
        ).first()

        if country is None:
            logger.warning(
                "Skipping channel '%s': country '%s' does not exist",
                record["name"],
                record["country_code"],
            )
            continue

        channel = Channel.objects.filter(
            name=record["name"],
            category=category,
            country=country,
        ).first()

        if channel is None:
            Channel.objects.create(
                id=uuid.uuid4(),
                name=record["name"],
                category=category,
                language=record["language"],
                country=country,
                urls=record["urls"],
            )
        else:
            channel.language = record["language"]
            channel.urls = record["urls"]
            channel.save(
                update_fields=[
                    "language",
                    "urls",
                ],
            )

        processed += 1

    return processed


@shared_task(
    bind=True,
    max_retries=3,
    time_limit=420,
    soft_time_limit=400,
)
def update_data(self) -> dict[str, int]:
    """
    Fetch and update countries, categories, and channels.

    Countries and channels are updated in one Celery task and one
    database transaction. The task does not depend on channel_service.
    """
    attempt = self.request.retries + 1

    logger.info(
        "Task update_data started: attempt %s/%s",
        attempt,
        self.max_retries + 1,
    )

    try:
        crawler = TVGardenCrawler()

        # Fetch both datasets before changing the database.
        countries = crawler.extract_countries()
        channels = crawler.extract_channels()

        # Keep countries and channels in the same database transaction.
        with transaction.atomic():
            countries_count = _update_countries(countries)
            channels_count = _update_channels(channels)

        result = {
            "countries": countries_count,
            "channels": channels_count,
        }

        logger.info(
            "Task update_data completed successfully: %s",
            result,
        )

        return result

    except Exception as exc:
        logger.exception(
            "Task update_data failed: attempt %s/%s",
            attempt,
            self.max_retries + 1,
        )

        raise self.retry(
            exc=exc,
            countdown=60,
        )
