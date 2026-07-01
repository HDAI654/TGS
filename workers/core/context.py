from contextlib import asynccontextmanager
from typing import AsyncGenerator
from workers.ports.crawler_interface import ICrawler
from workers.imp.tv_garden_crawler_imp import TVGardenCrawlerImp
from workers.core.database import get_async_session
from workers.ports.unit_of_work_interface import IUnitOfWork
from workers.imp.sqlal_unit_of_work import SQLAL_UnitOfWork


def get_crawler() -> ICrawler:
    return TVGardenCrawlerImp()


@asynccontextmanager
async def get_uow() -> AsyncGenerator[IUnitOfWork, None]:
    gen = get_async_session()

    try:
        session = await gen.__anext__()
        uow = SQLAL_UnitOfWork(session)
        yield uow
    finally:
        await gen.aclose()
