import logging
from src.modules.channels.domain.ports.unit_of_work_interface import IUnitOfWork
from src.modules.channels.domain.value_objects.id import ID
from src.modules.channels.exceptions import InvalidIDError, URLNotFoundError

logger = logging.getLogger(__name__)


class RemoveChannelURLsService:
    def __init__(
        self,
        uow: IUnitOfWork,
    ):
        self.uow = uow

    async def execute(self, url_id: str) -> None:
        logger.info("Removing url: url_id=%s", url_id)

        # Get url
        try:
            url_id_vo = ID(url_id)
        except InvalidIDError:
            raise URLNotFoundError(f"URL not found: url_id={url_id}")

        await self.uow.channels.remove_url(
            url_id=url_id_vo,
        )

        await self.uow.commit()

        logger.info("URL removed successfully: url_id=%s", url_id)
