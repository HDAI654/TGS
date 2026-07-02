import os
from dotenv import load_dotenv
from pathlib import Path

if os.getenv("APP_NAME", None) is not None:
    BASE_DIR = Path(__file__).resolve().parent.parent

    env_file = BASE_DIR / ".env"
    load_dotenv(env_file)


class Config:
    # App
    APP_NAME: str = os.getenv("APP_NAME", "MyApp")
    APP_ENV: str = os.getenv("APP_ENV", "development")

    # DB
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite+aiosqlite:///:memory:",
    )

    # Cache
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://redis:6379/0")
