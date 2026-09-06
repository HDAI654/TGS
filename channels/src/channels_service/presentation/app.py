from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from starlette.middleware.base import BaseHTTPMiddleware
from strawberry.fastapi import GraphQLRouter
from channels_service.config import APP_NAME, CORS_ALLOWED_ORIGINS
from channels_service.infrastructure.persistence.database import engine, session_factory
from channels_service.infrastructure.persistence.repositories import SQLAlchemyChannelRepository, SQLAlchemyCountryRepository
from channels_service.presentation.graphql.schema import schema


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()


class SessionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        session = session_factory()
        request.state.db_session = session
        try:
            return await call_next(request)
        finally:
            await session.close()


app = FastAPI(title=APP_NAME, lifespan=lifespan)
app.add_middleware(SessionMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def context_getter(request: Request):
    session = request.state.db_session
    return {
        "request": request,
        "session": session,
        "channel_repository": SQLAlchemyChannelRepository(session),
        "country_repository": SQLAlchemyCountryRepository(session),
    }


graphql_app = GraphQLRouter(schema, context_getter=context_getter)
app.include_router(graphql_app, prefix="/graphql")


@app.get("/health", tags=["health"])
async def health() -> dict[str, str]:
    async with session_factory() as session:
        await session.execute(text("SELECT 1"))
    return {"status": "healthy"}
