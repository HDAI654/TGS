import logging
from fastapi import FastAPI
from src.logging_config import setup_logging
from contextlib import asynccontextmanager
from src.core.database import engine, Base
from src.channel_app.presentation.graphql.v1 import graphql_v1_app
from src.core.conf import Config

setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(lifespan=lifespan)


@app.get("/", tags=["Root"])
async def read_root():
    return {"message": f"Welcome to {Config.APP_NAME}"}


app.include_router(graphql_v1_app)
