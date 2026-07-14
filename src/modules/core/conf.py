import os
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
env_file = BASE_DIR / ".env"

if os.getenv("APP_NAME", None) is None:
    load_dotenv(env_file)

PRIVATE_KEY_PATH = BASE_DIR / "keys" / "private.pem"
PUBLIC_KEY_PATH = BASE_DIR / "keys" / "public.pem"


class Config:
    # App
    APP_NAME: str = os.getenv("APP_NAME", "MyApp")
    APP_ENV: str = os.getenv("APP_ENV", "development")

    # Email
    SUPPORT_EMAIL: str = os.getenv("SUPPORT_EMAIL", f"support@{APP_NAME}.com")

    # Links
    VERIFY_EMAIL_URL: str = os.getenv(
        "VERIFY_EMAIL_URL", "http://localhost:8000/verifyemail"
    )
    VERIFY_EMAIL_EXPIRE_MINUTES: int = int(
        os.getenv("VERIFY_EMAIL_EXPIRE_MINUTES", 1440)
    )
    RESET_PASSWORD_URL: str = os.getenv(
        "RESET_PASSWORD_URL", "http://localhost:8000/reset-password"
    )
    RESET_PASSWORD_EXPIRE_MINUTES: int = int(
        os.getenv("RESET_PASSWORD_EXPIRE_MINUTES", 60)
    )

    # DB
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite+aiosqlite:///:memory:",
    )

    # Cache
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://redis:6379/0")
    SESSION_KEY_PREFIX: str = os.getenv("SESSION_KEY_PREFIX", "session:")
    USER_SESSIONS_KEY_PREFIX: str = os.getenv(
        "USER_SESSIONS_KEY_PREFIX", "user_sessions:"
    )

    # Auth Token
    AUTH_TOKEN_ALGORITHM: str = os.getenv("AUTH_TOKEN_ALGORITHM", "RS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 15))
    REFRESH_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES", 43200)
    )
    ROTATE_THRESHOLD_MINUTES: int = int(os.getenv("ROTATE_THRESHOLD_MINUTES", 4320))
    # Load keys
    with open(PRIVATE_KEY_PATH, "r") as f:
        AUTH_TOKEN_PRIVATE_KEY: str = f.read()

    with open(PUBLIC_KEY_PATH, "r") as f:
        AUTH_TOKEN_PUBLIC_KEY: str = f.read()

    # Email
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", 465))
    SMTP_USER: str = os.getenv("SMTP_USER", "your-email@gmail.com")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "xxxx xxxx xxxx xxxx")
    FROM_EMAIL: str = os.getenv("FROM_EMAIL", "your-email@gmail.com")
