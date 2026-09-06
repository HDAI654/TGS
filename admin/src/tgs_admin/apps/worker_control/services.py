from django.db import transaction
from django_celery_beat.models import IntervalSchedule, PeriodicTask
from .models import WorkerConfiguration

TASK_NAME = "update-data"
CELERY_TASK = "tgs_admin.apps.worker_control.tasks.update_data"


def get_configuration() -> WorkerConfiguration:
    configuration, _ = WorkerConfiguration.objects.get_or_create(
        pk=1,
        defaults={"interval_minutes": 30},
    )
    return configuration


@transaction.atomic
def update_schedule(interval_minutes: int) -> WorkerConfiguration:
    configuration = get_configuration()
    configuration.interval_minutes = interval_minutes
    configuration.save(update_fields=("interval_minutes", "updated_at"))

    schedule, _ = IntervalSchedule.objects.get_or_create(
        every=interval_minutes,
        period=IntervalSchedule.MINUTES,
    )
    PeriodicTask.objects.update_or_create(
        name=TASK_NAME,
        defaults={
            "interval": schedule,
            "task": CELERY_TASK,
            "enabled": True,
        },
    )
    return configuration


def ensure_schedule() -> None:
    configuration = get_configuration()
    update_schedule(configuration.interval_minutes)
