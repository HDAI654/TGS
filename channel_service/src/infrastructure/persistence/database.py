"""Async SQLAlchemy engine and session factory.

Timeouts are applied at the connection level. Session lifecycle is owned by
the presentation composition root (per-request middleware).
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.conf import DATABASE_URL

engine = create_async_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=1800,
    connect_args={"timeout": 5, "command_timeout": 10},
)
session_factory = async_sessionmaker(engine, expire_on_commit=False)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield a database session for a single request scope."""
    async with session_factory() as session:
        yield session
