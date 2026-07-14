import logging
from src.modules.channels.domain.ports.unit_of_work_interface import IUnitOfWork
from src.modules.channels.domain.entities.channel import ChannelEntity
from src.modules.channels.exceptions import CountryNotFoundError

logger = logging.getLogger(__name__)


class CreateChannelService:
    def __init__(
        self,
        uow: IUnitOfWork,
    ):
        self.uow = uow

    async def execute(
        self,
        name: str,
        category: str,
        language: str,
        country_code: str,
        is_geo_blocked: bool,
        **kwargs,
    ) -> ChannelEntity:
        logger.info("Creating channel: name=%s, country_code=%s", name, country_code)

        # Create channel entity
        channel = ChannelEntity.create(
            name=name,
            category=category,
            language=language,
            country_code=country_code,
            is_geo_blocked=is_geo_blocked,
        )

        if await self.uow.countries.exists_by_code(channel.country_code) is False:
            raise CountryNotFoundError(
                f"Country not found: country_code={channel.country_code.value}"
            )

        await self.uow.channels.add(channel)
        await self.uow.commit()

        logger.info("Channel created successfully: channel_id=%s", channel.id.value)
        return channel
