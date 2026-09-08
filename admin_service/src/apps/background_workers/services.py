from __future__ import annotations
from django_celery_beat.models import IntervalSchedule, PeriodicTask

TASK_NAME = "Update categories, countries, and channels"
TASK_PATH = "src.apps.background_workers.tasks.update_data"


def get_or_create_task() -> PeriodicTask:
    """Get the update-data periodic task, creating it if necessary."""
    task, _ = PeriodicTask.objects.get_or_create(
        name=TASK_NAME,
        defaults={
            "task": TASK_PATH,
            "enabled": False,
        },
    )

    return task


def start_worker() -> PeriodicTask:
    """Enable the background worker."""
    task = get_or_create_task()
    task.enabled = True
    task.save(update_fields=["enabled"])

    return task


def stop_worker() -> PeriodicTask:
    """Disable the background worker."""
    task = get_or_create_task()
    task.enabled = False
    task.save(update_fields=["enabled"])

    return task


def restart_worker(interval_minutes: int) -> PeriodicTask:
    """Update the interval and enable the background worker."""
    if interval_minutes <= 0:
        raise ValueError("Interval must be greater than zero.")

    schedule, _ = IntervalSchedule.objects.get_or_create(
        every=interval_minutes,
        period=IntervalSchedule.MINUTES,
    )

    task = get_or_create_task()
    task.interval = schedule
    task.enabled = True
    task.save(update_fields=["interval", "enabled"])

    return task


def get_worker_status() -> dict:
    """Return the current background worker status."""
    task = get_or_create_task()

    interval_minutes = None

    if task.interval:
        interval_minutes = (
            task.interval.every
            if task.interval.period == IntervalSchedule.MINUTES
            else None
        )

    return {
        "running": task.enabled,
        "interval_minutes": interval_minutes,
        "task": task.task,
    }
