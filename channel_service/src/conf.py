"""Environment-driven configuration for the channels service.

Validated at import time for required values. Application and Domain never
select infrastructure implementations from environment variables.
"""

import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
APP_NAME = os.getenv("APP_NAME", "TGS Channels")
APP_ENV = os.getenv("APP_ENV", "production")
CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CORS_ALLOWED_ORIGINS", "*").split(",")
    if origin.strip()
]
