import pytest
from django_celery_beat.models import IntervalSchedule, PeriodicTask

from tgs_admin.apps.worker_control.services import get_configuration, update_schedule

pytestmark = pytest.mark.django_db


def test_update_schedule_persists_configuration_and_periodic_task():
    configuration = update_schedule(15)

    assert configuration.pk == 1
    assert configuration.interval_minutes == 15
    task = PeriodicTask.objects.get(name="update-data")
    assert task.enabled is True
    assert task.task == "tgs_admin.apps.worker_control.tasks.update_data"
    assert task.interval.every == 15
    assert task.interval.period == IntervalSchedule.MINUTES


def test_update_schedule_reuses_the_single_periodic_task():
    update_schedule(15)
    update_schedule(30)

    assert PeriodicTask.objects.filter(name="update-data").count() == 1
    assert get_configuration().interval_minutes == 30
    assert PeriodicTask.objects.get(name="update-data").interval.every == 30
