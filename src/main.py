from fastapi import FastAPI
from src.logging_config import setup_logging
from contextlib import asynccontextmanager
from src.modules.core.database import engine
from src.modules.core.database import Base
from src.modules.core.redis_client import close_redis_client
import logging
from src.modules.core.conf import Config
from src.modules.auth.presentation.api.v1 import router as router_v1_auth
from src.modules.channels.presentation.graphql.v1 import graphql_router_v1_channels
from src.modules.channels.presentation.api.v1.router import (
    router as rest_router_v1_channels,
)

setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await close_redis_client()
    await engine.dispose()


app = FastAPI(
    lifespan=lifespan,
)

logging.info("%s started successfully", Config.APP_NAME)


@app.get("/", tags=["Root"])
async def read_root():
    return {"message": f"Welcome to {Config.APP_NAME}"}


app.include_router(router_v1_auth)
app.include_router(graphql_router_v1_channels)
app.include_router(rest_router_v1_channels)
