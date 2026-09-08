import os
from pathlib import Path
import dj_database_url

# ===== APP =====

APP_NAME = os.getenv("APP_NAME", "TGS")
APP_ENV = os.getenv("APP_ENV", "development")
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "django-secret")

DEBUG = os.getenv("DJANGO_DEBUG", "false").lower() == "true"


# ===== HOST / SECURITY =====

ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv("DJANGO_ALLOWED_HOSTS", "*").split(",")
    if host.strip()
]

CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",")
    if origin.strip()
]


# ===== APPS =====

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_celery_beat",
    "src.apps.categories",
    "src.apps.countries",
    "src.apps.channels",
    "src.apps.monitoring",
    "src.apps.background_workers"
]


# ===== MIDDLEWARE =====

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# ===== TEMPLATES =====

ROOT_URLCONF = "src.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "src" / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


# ===== WSGI =====

WSGI_APPLICATION = "src.wsgi.application"


# ===== DATABASE =====

if os.environ.get("APP_ENV", "development") == "development":
    # Use SQLite for development
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
        }
    }
else:
    # Use PostgreSQL for production
    DATABASES = {
        "default": dj_database_url.parse(
            os.environ["DATABASE_URL"],
            conn_max_age=600,
        )
    }


# ===== INTERNATIONALIZATION =====

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# ===== AUTHENTICATION =====

LOGIN_URL = "/admin/login/"
LOGIN_REDIRECT_URL = "/admin/"
LOGOUT_REDIRECT_URL = "/admin/login/"

# ===== LOGGING =====

LOGS_DIR = BASE_DIR / "logs"
LOG_FILE = LOGS_DIR / "app.log"

LOGS_DIR.mkdir(exist_ok=True)

if APP_ENV == "development":
    ROOT_LOG_LEVEL = "DEBUG"
    CONSOLE_LOG_LEVEL = "DEBUG"
    FILE_LOG_LEVEL = "INFO"
else:
    ROOT_LOG_LEVEL = "INFO"
    CONSOLE_LOG_LEVEL = "ERROR"
    FILE_LOG_LEVEL = "INFO"


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": CONSOLE_LOG_LEVEL,
            "formatter": "standard",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": FILE_LOG_LEVEL,
            "formatter": "standard",
            "filename": str(LOG_FILE),
            "maxBytes": 20 * 1024 * 1024,
            "backupCount": 3,
            "encoding": "utf-8",
        },
    },
    "root": {
        "level": ROOT_LOG_LEVEL,
        "handlers": (["console"] if ROOT_LOG_LEVEL == "DEBUG" else ["console", "file"]),
    },
}

# ===== STATIC FILES =====

STATIC_URL = "/static/"

# Directory where static files will be collected (for production)
STATIC_ROOT = BASE_DIR / "staticfiles"

# Additional directories where Django will look for static files
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

# ===== MEDIA FILES =====

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ===== CELERY =====
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://127.0.0.1:6379/0")
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"