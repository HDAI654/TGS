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

    with open(BASE_DIR / "timezones.json", "r", encoding="utf-8") as f:
        ALLOWED_TIMEZONE = set(json.load(f)["timezones"])

    with open(BASE_DIR / "languages.json", "r", encoding="utf-8") as f:
        ALLOWED_LANGUAGES = set(json.load(f)["languages"])

    # DB
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite+aiosqlite:///:memory:",
    )
