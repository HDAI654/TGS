from shared.domain.ports.unit_of_work_interface import IUnitOfWork
from src.channel_app.infrastructure.persistence.sqlal_unit_of_work import (
    SQLAL_UnitOfWork,
)
from src.core.database import get_async_session


async def get_graphql_context():
    """Create GraphQL context with UOW."""
    async for db in get_async_session():
        uow: IUnitOfWork = SQLAL_UnitOfWork(db)
        yield {"uow": uow}
