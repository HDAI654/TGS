import logging
from shared.domain.ports.unit_of_work_interface import IUnitOfWork
from shared.domain.id_vo import ID
from src.core.exceptions import InvalidIDError, ChannelNotFoundError

logger = logging.getLogger(__name__)


class DeleteChannelService:
    def __init__(
        self,
        uow: IUnitOfWork,
    ):
        self.uow = uow

    async def execute(self, channel_id: str) -> None:
        logger.info("Deleting channel: channel_id=%s", channel_id)

        # Get channel
        try:
            channel_id_vo = ID(channel_id)
        except InvalidIDError:
            raise ChannelNotFoundError(f"Channel not found: channel_id={channel_id}")

        await self.uow.channels.delete(channel_id_vo)
        await self.uow.commit()

        logger.info("Channel deleted successfully: channel_id=%s", channel_id)
