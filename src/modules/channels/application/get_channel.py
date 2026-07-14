import logging
from src.modules.channels.domain.ports.unit_of_work_interface import IUnitOfWork
from src.modules.channels.domain.entities.channel import ChannelEntity
from src.modules.channels.domain.value_objects.id import ID
from src.modules.channels.exceptions import InvalidIDError, ChannelNotFoundError

logger = logging.getLogger(__name__)


class GetChannelService:
    def __init__(
        self,
        uow: IUnitOfWork,
    ):
        self.uow = uow

    async def execute(self, channel_id: str) -> ChannelEntity:
        logger.info("Getting channel: channel_id=%s", channel_id)

        # Get channel
        try:
            channel_id_vo = ID(channel_id)
        except InvalidIDError:
            raise ChannelNotFoundError(f"Channel not found: channel_id={channel_id}")
        channel = await self.uow.channels.get_by_id(channel_id_vo)

        logger.info("Channel found successfully: channel_id=%s", channel_id)

        return channel
