import logging
from src.modules.channels.domain.ports.unit_of_work_interface import IUnitOfWork
from src.modules.channels.domain.entities.url_entity import URLEntity
from src.modules.channels.domain.value_objects.id import ID
from src.modules.channels.exceptions import InvalidIDError, ChannelNotFoundError

logger = logging.getLogger(__name__)


class AddChannelURLsService:
    def __init__(
        self,
        uow: IUnitOfWork,
    ):
        self.uow = uow

    async def execute(self, channel_id: str, url_link: str) -> None:
        logger.info("Adding url to channel: channel_id=%s", channel_id)

        # Get channel
        try:
            channel_id_vo = ID(channel_id)
        except InvalidIDError:
            raise ChannelNotFoundError(f"Channel not found: channel_id={channel_id}")

        url = URLEntity.create(url=url_link)

        await self.uow.channels.add_new_url(
            channel_id=channel_id_vo,
            url=url,
        )

        await self.uow.commit()

        logger.info(
            "URL added successfully: channel_id=%s url_id=%s", channel_id, url.id.value
        )
