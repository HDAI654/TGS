import logging
from src.channel_app.domain.ports.unit_of_work_interface import IUnitOfWork
from src.core.id_vo import ID
from src.channel_app.domain.value_objects.name import Name
from src.channel_app.domain.value_objects.category import Category
from src.channel_app.domain.value_objects.country_code import CountryCode
from src.channel_app.domain.value_objects.is_geo_blocked import IsGeoBlocked
from src.core.exceptions import InvalidIDError, ChannelNotFoundError

logger = logging.getLogger(__name__)


class EditChannelService:
    def __init__(
        self,
        uow: IUnitOfWork,
    ):
        self.uow = uow

    async def execute(
        self,
        channel_id: str,
        new_name: str | None = None,
        new_category: str | None = None,
        new_country_code: str | None = None,
        new_is_geo_blocked: bool | None = None,
    ) -> None:
        logger.info("Editing channel: channel_id=%s", channel_id)

        # Get channel
        try:
            channel_id_vo = ID(channel_id)
        except InvalidIDError:
            raise ChannelNotFoundError(f"Channel not found: channel_id={channel_id}")

        # Convert optional parameters to value objects
        new_name_vo = Name(new_name) if new_name is not None else None
        new_category_vo = Category(new_category) if new_category is not None else None
        new_country_code_vo = (
            CountryCode(new_country_code) if new_country_code is not None else None
        )
        new_is_geo_blocked_vo = (
            IsGeoBlocked(new_is_geo_blocked) if new_is_geo_blocked is not None else None
        )

        await self.uow.channels.update(
            channel_id=channel_id_vo,
            new_name=new_name_vo,
            new_category=new_category_vo,
            new_country_code=new_country_code_vo,
            new_is_geo_blocked=new_is_geo_blocked_vo,
        )
        await self.uow.commit()

        logger.info("Channel updated successfully: channel_id=%s", channel_id)
