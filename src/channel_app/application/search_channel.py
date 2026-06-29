import logging
from typing import Any
from src.channel_app.domain.ports.unit_of_work_interface import IUnitOfWork
from src.channel_app.domain.entities.channel import ChannelEntity
from src.channel_app.domain.factories.channel_factory import ChannelFactory

logger = logging.getLogger(__name__)


class SearchChannelService:
    def __init__(
        self,
        uow: IUnitOfWork,
    ):
        self.uow = uow

    async def execute(self, filters: dict[str, Any]) -> list[ChannelEntity]:
        logger.info("Searching for channels: filters=%s", filters)

        channels = await self.uow.channels.search(
            filters=filters,
        )

        logger.info("Successfully found %s channels", len(channels))

        return channels
