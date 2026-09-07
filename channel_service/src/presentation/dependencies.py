"""Composition helpers for request-scoped dependencies.

Concrete repositories are constructed here from the request session.
Use cases receive ports only.
"""

from fastapi import Request

from src.infrastructure.persistence.repositories import (
    SQLAlchemyChannelRepository,
    SQLAlchemyCountryRepository,
)


def build_graphql_context(request: Request) -> dict:
    """Build the GraphQL context with injected read repositories."""
    session = request.state.db_session
    return {
        "request": request,
        "session": session,
        "channel_repository": SQLAlchemyChannelRepository(session),
        "country_repository": SQLAlchemyCountryRepository(session),
    }
