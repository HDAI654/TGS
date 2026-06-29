import logging
from shared.domain.ports.unit_of_work_interface import IUnitOfWork
from shared.domain.entities.url_entity import URLEntity
from src.core.id_vo import ID
from src.core.exceptions import InvalidIDError, ChannelNotFoundError

logger = logging.getLogger(__name__)


class GetChannelURLsService:
    def __init__(
        self,
        uow: IUnitOfWork,
    ):
        self.uow = uow

    async def execute(self, channel_id: str) -> list[URLEntity]:
        logger.info("Getting channel urls: channel_id=%s", channel_id)

        # Get channel
        try:
            channel_id_vo = ID(channel_id)
        except InvalidIDError:
            raise ChannelNotFoundError(f"Channel not found: channel_id={channel_id}")

        urls = await self.uow.channels.get_urls(channel_id_vo)

        logger.info(
            "Channel urls found successfully: channel_id=%s url_count=%s",
            channel_id,
            len(urls),
        )

        return urls
