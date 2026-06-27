import logging
from src.channel_app.domain.ports.unit_of_work_interface import IUnitOfWork
from src.channel_app.domain.entities.channel import ChannelEntity
from src.channel_app.domain.factories.channel_factory import ChannelFactory

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
        channel = ChannelFactory.create(
            name=name,
            category=category,
            language=language,
            country_code=country_code,
            is_geo_blocked=is_geo_blocked,
        )

        await self.uow.channels.add(channel)
        await self.uow.commit()

        logger.info("Channel created successfully: channel_id=%s", channel.id.value)
        return channel
