import os

DATABASE_URL = os.environ["DATABASE_URL"]
APP_NAME = os.getenv("APP_NAME", "TGS Channels")
CORS_ALLOWED_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS", "*").split(",")
