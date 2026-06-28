import strawberry
import logging
from typing import Optional
from src.channel_app.presentation.graphql.v1.channel.types import ChannelType
from src.channel_app.domain.ports.unit_of_work_interface import IUnitOfWork
from src.channel_app.application.create_channel import CreateChannelService
from src.channel_app.application.edit_channel import EditChannelService
from src.channel_app.application.delete_channel import DeleteChannelService
from src.channel_app.application.add_channel_url import AddChannelURLsService
from src.channel_app.application.remove_channel_url import RemoveChannelURLsService
from src.channel_app.presentation.graphql.v1.error_handler import error_handler
from src.core.exceptions import (
    ChannelNotFoundError,
    ChannelDuplicateError,
    URLNotFoundError,
    URLDuplicateError,
    NoChangesError,
)
from src.channel_app.presentation.graphql.v1.error_code import ErrorCodes

logger = logging.getLogger(__name__)


@strawberry.type
class ChannelMutation:
    @strawberry.mutation
    @error_handler(
        "create_channel",
        logger,
        {
            ChannelDuplicateError: (None, ErrorCodes.DUPLICATE_CHANNEL, 409),
        },
    )
    async def create_channel(
        self,
        name: str,
        category: str,
        language: str,
        country_code: str,
        is_geo_blocked: bool,
        info: strawberry.Info,
    ) -> ChannelType:
        logger.info("GraphQL: Creating channel: name=%s", name)
        uow: IUnitOfWork = info.context.get("uow")
        service = CreateChannelService(uow)
        entity = await service.execute(
            name=name,
            category=category,
            language=language,
            country_code=country_code,
            is_geo_blocked=is_geo_blocked,
        )
        return ChannelType.from_entity(entity)

    @strawberry.mutation
    @error_handler(
        "update_channel",
        logger,
        {
            ChannelNotFoundError: (
                None,
                ErrorCodes.CHANNEL_NOT_FOUND,
                404,
            ),
            NoChangesError: (
                None,
                ErrorCodes.NO_CHANGES_ERROR,
                400,
            ),
            ChannelDuplicateError: (None, ErrorCodes.DUPLICATE_CHANNEL, 409),
        },
    )
    async def update_channel(
        self,
        channel_id: str,
        info: strawberry.Info,
        new_name: Optional[str] = None,
        new_category: Optional[str] = None,
        new_country_code: Optional[str] = None,
        new_is_geo_blocked: Optional[bool] = None,
    ) -> bool:
        logger.info("GraphQL: Updating channel: id=%s", channel_id)
        uow: IUnitOfWork = info.context.get("uow")
        service = EditChannelService(uow)
        await service.execute(
            channel_id=channel_id,
            new_name=new_name,
            new_category=new_category,
            new_country_code=new_country_code,
            new_is_geo_blocked=new_is_geo_blocked,
        )
        return True

    @strawberry.mutation
    @error_handler(
        "delete_channel",
        logger,
        {
            ChannelNotFoundError: (
                None,
                ErrorCodes.CHANNEL_NOT_FOUND,
                404,
            )
        },
    )
    async def delete_channel(
        self,
        channel_id: str,
        info: strawberry.Info,
    ) -> bool:
        logger.info("GraphQL: Deleting channel: id=%s", channel_id)
        uow: IUnitOfWork = info.context.get("uow")
        service = DeleteChannelService(uow)
        await service.execute(channel_id)
        return True

    @strawberry.mutation
    @error_handler(
        "add_channel_url",
        logger,
        {
            URLDuplicateError: (None, ErrorCodes.DUPLICATE_URL, 409),
        },
    )
    async def add_channel_url(
        self,
        channel_id: str,
        url: str,
        info: strawberry.Info,
    ) -> bool:
        logger.info("GraphQL: Adding URL to channel: id=%s", channel_id)
        uow: IUnitOfWork = info.context.get("uow")
        service = AddChannelURLsService(uow)
        await service.execute(channel_id, url)
        return True

    @strawberry.mutation
    @error_handler(
        "remove_channel_url",
        logger,
        {
            URLNotFoundError: (
                None,
                ErrorCodes.URL_NOT_FOUND,
                404,
            )
        },
    )
    async def remove_channel_url(
        self,
        url_id: str,
        info: strawberry.Info,
    ) -> bool:
        logger.info("GraphQL: Removing URL: id=%s", url_id)
        uow: IUnitOfWork = info.context.get("uow")
        service = RemoveChannelURLsService(uow)
        await service.execute(url_id)
        return True
