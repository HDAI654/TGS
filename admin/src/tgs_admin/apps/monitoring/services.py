import os
import time
from collections import deque
from datetime import timedelta
from pathlib import Path
from typing import Any

import psutil
from celery.exceptions import CeleryError
from urllib.error import URLError
from urllib.request import Request, urlopen
from celery.app.control import Inspect
from django.utils import timezone
from django_celery_beat.models import PeriodicTask
from tgs_admin.celery import app

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


def worker_status() -> dict[str, Any]:
    inspector: Inspect = app.control.inspect(timeout=1)
    try:
        active = inspector.active() or {}
        registered = inspector.registered() or {}
    except (CeleryError, OSError):
        return {
            "count": 0,
            "workers": [],
            "active_tasks": 0,
            "status": "unreachable",
            "expected_count": 1,
            "schedule": _schedule_status(),
        }

    workers = sorted(set(active) | set(registered))
    worker_count = len(workers)
    return {
        "count": worker_count,
        "workers": workers,
        "active_tasks": sum(len(tasks) for tasks in active.values()),
        "status": "healthy" if worker_count == 1 else "unhealthy",
        "expected_count": 1,
        "schedule": _schedule_status(),
    }


def _schedule_status() -> dict[str, Any]:
    periodic_task = (
        PeriodicTask.objects.filter(name="update-data")
        .select_related("interval")
        .first()
    )
    if periodic_task is None or periodic_task.interval is None:
        return {"configured": False}

    last_run_at = periodic_task.last_run_at
    next_run_at = None
    if last_run_at is not None:
        next_run_at = last_run_at + timedelta(
            **{periodic_task.interval.period: periodic_task.interval.every}
        )
    elif periodic_task.start_time is not None:
        next_run_at = periodic_task.start_time

    return {
        "configured": True,
        "enabled": periodic_task.enabled,
        "interval": f"Every {periodic_task.interval.every} {periodic_task.interval.period}",
        "last_run_at": last_run_at,
        "next_run_at": next_run_at,
        "overdue": bool(next_run_at and next_run_at < timezone.now()),
    }


def recent_logs(limit: int = 100) -> list[str]:
    log_path = Path(os.getenv("LOG_FILE", "/app/logs/admin.log"))
    if not log_path.exists():
        return []
    with log_path.open(encoding="utf-8", errors="replace") as log_file:
        return list(deque(log_file, maxlen=limit))
