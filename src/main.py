import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.logging_config import setup_logging
from contextlib import asynccontextmanager
from src.core.database import engine, Base
from src.channel_app.presentation.graphql.v1 import graphql_v1_app
from src.channel_app.presentation.api.v1.router import router as rest_v1_router
from src.core.conf import Config

setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Creating tables ...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Tables created successfully")

    yield

    logger.info("Closing DB engine")
    await engine.dispose()
    logger.info("DB engine closed successfully")


app = FastAPI(lifespan=lifespan)

# !! Only for test !!
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Root"])
async def read_root():
    return {"message": f"Welcome to {Config.APP_NAME}"}


app.include_router(graphql_v1_app)
app.include_router(rest_v1_router)
