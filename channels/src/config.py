import os

APP_NAME = os.getenv("APP_NAME", "TGS Channels")
DATABASE_URL = os.environ["DATABASE_URL"]
CORS_ALLOWED_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS", "*").split(",")
