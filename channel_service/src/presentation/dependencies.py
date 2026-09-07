"""Composition helpers for request-scoped dependencies."""

from fastapi import Request

from src.conf import APP_ENV
from src.infrastructure.persistence.repositories import (
    SQLAlchemyChannelRepository,
    SQLAlchemyCountryRepository,
)

if APP_ENV == "development":
    from src.infrastructure.persistence.in_memory_seed import (
        channel_repo as in_memory_channel_repo,
        country_repo as in_memory_country_repo,
    )


def build_graphql_context(request: Request) -> dict:
    """Build the GraphQL context with injected read repositories."""
    if APP_ENV == "development":
        # Use in-memory repositories (ignore the request session)
        return {
            "request": request,
            "session": None,  # optional
            "channel_repository": in_memory_channel_repo,
            "country_repository": in_memory_country_repo,
        }
    else:
        # Production: use SQLAlchemy repositories with the request session
        session = request.state.db_session
        return {
            "request": request,
            "session": session,
            "channel_repository": SQLAlchemyChannelRepository(session),
            "country_repository": SQLAlchemyCountryRepository(session),
        }
