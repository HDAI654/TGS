from fastapi import FastAPI
from src.logging_config import setup_logging
from contextlib import asynccontextmanager
from src.modules.core.database import engine
from src.modules.core.database import Base
from src.modules.core.redis_client import close_redis_client
import logging
from src.modules.core.conf import Config
from src.modules.auth.presentation.api.v1 import router as router_v1_auth

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
