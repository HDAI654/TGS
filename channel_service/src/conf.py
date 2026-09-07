"""Environment-driven configuration for the channels service."""

import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

_env = BASE_DIR / ".env"
if os.getenv("APP_NAME") is None and _env.exists():
    load_dotenv(_env)


class Config:
    APP_NAME: str = os.getenv("APP_NAME", "TGS")
    APP_ENV: str = os.getenv("APP_ENV", "development")

    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///:memory:")

    CORS_ALLOWED_ORIGINS = [
        origin.strip()
        for origin in os.getenv("CORS_ALLOWED_ORIGINS", "*").split(",")
        if origin.strip()
    ]
