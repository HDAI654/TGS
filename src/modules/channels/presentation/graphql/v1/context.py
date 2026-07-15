from src.modules.channels.domain.ports.unit_of_work_interface import IUnitOfWork
from src.modules.channels.infrastructure.persistence.sqlal_unit_of_work import (
    SQLAL_UnitOfWork,
)
from src.modules.core.database import get_async_session


async def get_graphql_context():
    """Create GraphQL context with UOW."""
    async for db in get_async_session():
        uow: IUnitOfWork = SQLAL_UnitOfWork(db)
        yield {"uow": uow}
