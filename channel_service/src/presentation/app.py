"""FastAPI presentation adapter for the channels service."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from starlette.middleware.base import BaseHTTPMiddleware
from strawberry.fastapi import GraphQLRouter

from src.conf import APP_NAME, CORS_ALLOWED_ORIGINS, APP_ENV
from src.presentation.dependencies import build_graphql_context
from src.presentation.graphql.schema import schema

logger = logging.getLogger(__name__)

if APP_ENV != "development":
    from src.database import engine, session_factory

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        yield
        await engine.dispose()

    class SessionMiddleware(BaseHTTPMiddleware):
        """Attach a request-scoped AsyncSession and close it after the response."""

        async def dispatch(self, request: Request, call_next):
            session = session_factory()
            request.state.db_session = session
            try:
                return await call_next(request)
            finally:
                await session.close()


# Add session middleware only in production (or when using a real DB)
if APP_ENV != "development":
    app = FastAPI(title=APP_NAME, lifespan=lifespan)
    app.add_middleware(SessionMiddleware)
else:
    app = FastAPI(title=APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

graphql_app = GraphQLRouter(schema, context_getter=build_graphql_context)
app.include_router(graphql_app, prefix="/graphql")


@app.get("/health", tags=["health"])
async def health() -> dict[str, str]:
    """Liveness/readiness probe."""
    if APP_ENV == "development":
        # In-memory repositories are always "healthy"
        return {"status": "healthy"}
    # Production: verify database connectivity
    async with session_factory() as session:
        await session.execute(text("SELECT 1"))
    return {"status": "healthy"}
