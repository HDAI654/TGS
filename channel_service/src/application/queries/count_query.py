from src.domain.ports.country_repository import CountryRepository
from src.domain.ports.channel_repository import ChannelRepository


async def get_count(
    country_repository: CountryRepository,
    channel_repository: ChannelRepository,
) -> dict:
    channels_count = await channel_repository.count_channels()
    countries_count = await country_repository.count_countries()
    return {
        "channels": channels_count,
        "countries": countries_count,
    }
