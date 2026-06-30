import os
from dotenv import load_dotenv
from pathlib import Path
import json

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env_file = BASE_DIR / ".env"
load_dotenv(env_file)


class Config:
    # App
    APP_NAME = os.getenv("APP_NAME", "MyApp")
    APP_ENV: str = os.getenv("APP_ENV", "development")

    # DB
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite+aiosqlite:///:memory:",
    )
