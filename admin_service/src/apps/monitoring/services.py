import os
import time
from collections import deque
from pathlib import Path
from typing import Any

import psutil
from urllib.error import URLError
from urllib.request import Request, urlopen
from django.conf import settings

CHANNELS_HEALTH_URL = os.getenv("CHANNELS_HEALTH_URL", "http://channels:8000/health")


def system_status() -> dict[str, Any]:
    return {
        "cpu_percent": psutil.cpu_percent(interval=0.1),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage("/").percent,
        "uptime_seconds": int(time.time() - psutil.boot_time()),
    }


def channels_status() -> dict[str, Any]:
    started = time.perf_counter()
    try:
        request = Request(CHANNELS_HEALTH_URL, method="GET")
        with urlopen(request, timeout=3) as response:
            status_code = response.status
        return {
            "status": "healthy" if 200 <= status_code < 300 else "unhealthy",
            "http_status": status_code,
            "latency_ms": round((time.perf_counter() - started) * 1000, 2),
        }
    except (URLError, TimeoutError, OSError) as exc:
        return {"status": "unreachable", "error": str(exc)}


def recent_logs(limit: int = 100) -> list[str]:
    log_path = settings.LOG_FILE
    if not log_path.exists():
        return []
    with log_path.open(encoding="utf-8", errors="replace") as log_file:
        return list(deque(log_file, maxlen=limit))
