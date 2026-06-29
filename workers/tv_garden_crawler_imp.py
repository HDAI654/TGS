import logging
from workers.crawler_interface import ICrawler
from shared.domain.entities.channel import ChannelEntity
from shared.domain.entities.country import CountryEntity
from shared.domain.factories.channel_factory import ChannelFactory
from shared.domain.factories.country_factory import CountryFactory
from shared.domain.factories.url_factory import URLFactory
from shared.domain.exceptions import DomainError
import httpx
import zlib
import json

logger = logging.getLogger(__name__)


class TVGardenCrawlerImp(ICrawler):
    """Implementation Crawler using tv-garden data."""

    COUNTRIES_URL = "https://tvgarden.world/api/tv/countries_metadata.json"
    CATEGORIES_URL = "https://tvgarden.world/api/tv/categories/{category}"
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

    async def extract_all_countries(self) -> list[CountryEntity]:
        logger.debug("Updating countries data")
        async with httpx.AsyncClient() as client:
            response = await client.get(self.CATEGORIES_URL)
            decompressed_data = self._decompressor(response)

            countries = []

            for code, data in decompressed_data.items():
                country_entity = CountryFactory.create(
                    country_code=str(code),
                    country_name=str(data.get("country")),
                    capital=str(data.get("capital")),
                    timezone=str(data.get("timeZone")),
                    channel_count=int(data.get("channelCount")),
                )
                countries.append(country_entity)

    async def extract_all_channels(self) -> list[ChannelEntity]:
        logger.info("Updating channels data")

        channels_data = {}

        for category_name, category_code in self.AVAILABLE_CATEGORIES.items():
            logger.debug("Updating channels of category=%s", category_name)
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.CATEGORIES_URL.format(category=category_code)
                )
                decompressed_data = self._decompressor(response)
                if decompressed_data == False:
                    logger.warning(
                        "Updating channels of category=%s failed", category_name
                    )
                    continue

                for ch in decompressed_data:
                    ch_entity = ChannelFactory.create(
                        id=str(ch.get("nano_id")),
                        name=str(ch.get("name")),
                        category=category_name,
                        language=str(ch.get("languages")[0]),
                        country_code=ch.get("country"),
                        is_geo_blocked=bool(ch.get("isGeoBlocked")),
                    )
                    urls_entity = [
                        URLFactory.create(url=u)
                        for u in ch.get("stream_urls") + ch.get("youtube_urls")
                    ]
                    channels_data[ch_entity.id.value] = {
                        "channel": ch_entity,
                        "urls": urls_entity,
                    }

    def _decompressor(self, response: httpx.Response):
        logger.info("Decompressing response's content")
        try:
            # Decompress the response content
            decompressed_data = zlib.decompress(response.content, 16 + zlib.MAX_WBITS)
            json_string = decompressed_data.decode("utf-8")
            data = json.loads(json_string)

            logger.info("Response's content decompressed successfully")

            return data
        except zlib.error as e:
            logger.info("Decompress failed, checking if it's already JSON")
            try:
                # If it is already JSON
                data = response.json()
                logger.info(
                    "Response's content decompressed successfully, It was JSON :)"
                )
                return data
            except:
                logger.error("Decompress failed, response's content is not acceptable")

            return False
