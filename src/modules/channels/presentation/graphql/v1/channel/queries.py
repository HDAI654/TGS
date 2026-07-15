import strawberry
import logging
from strawberry.scalars import JSON
from src.modules.channels.presentation.graphql.v1.channel.types import (
    ChannelType,
    URLType,
)
from src.modules.channels.domain.ports.unit_of_work_interface import IUnitOfWork
from src.modules.channels.application.get_channel import GetChannelService
from src.modules.channels.application.search_channel import SearchChannelService
from src.modules.channels.application.get_channel_urls import GetChannelURLsService
from src.modules.channels.presentation.graphql.v1.error_handler import error_handler
from src.modules.channels.exceptions import ChannelNotFoundError, InvalidFieldError
from src.modules.channels.presentation.graphql.v1.error_code import ErrorCodes

logger = logging.getLogger(__name__)


@strawberry.type
class ChannelQuery:
    @strawberry.field
    @error_handler(
        "get_channel",
        logger,
        {
            ChannelNotFoundError: (
                None,
                ErrorCodes.CHANNEL_NOT_FOUND,
                404,
            )
        },
    )
    async def channel(
        self,
        channel_id: str,
        info: strawberry.Info,
    ) -> ChannelType:
        logger.info("GraphQL: Getting channel: id=%s", channel_id)
        uow: IUnitOfWork = info.context.get("uow")
        service = GetChannelService(uow)
        entity = await service.execute(channel_id)
        return ChannelType.from_entity(entity)

    @strawberry.field
    @error_handler(
        "search_channels",
        logger,
        {
            InvalidFieldError: (
                None,
                ErrorCodes.INVALID_FIELD_ERROR,
                404,
            )
        },
    )
    async def channels(
        self,
        info: strawberry.Info,
        filters: JSON | None = None,
    ) -> list[ChannelType]:
        logger.info("GraphQL: Searching channels: filters=%s", filters)
        uow: IUnitOfWork = info.context.get("uow")
        service = SearchChannelService(uow)
        results = await service.execute(filters or {})
        return [ChannelType.from_entity(r) for r in results]

    @strawberry.field
    @error_handler(
        "get_channel_urls",
        logger,
        {
            ChannelNotFoundError: (
                None,
                ErrorCodes.CHANNEL_NOT_FOUND,
                404,
            )
        },
    )
    async def channel_urls(
        self,
        channel_id: str,
        info: strawberry.Info,
    ) -> list[URLType]:
        logger.info("GraphQL: Getting URLs for channel: id=%s", channel_id)
        uow: IUnitOfWork = info.context.get("uow")
        service = GetChannelURLsService(uow)
        urls = await service.execute(channel_id)
        return [URLType.from_entity(u) for u in urls]
