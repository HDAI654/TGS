import pytest
pytestmark = pytest.mark.django_db


def test_worker_configuration_form_rejects_zero():
    from tgs_admin.apps.worker_control.forms import WorkerConfigurationForm
    assert not WorkerConfigurationForm(data={"interval_minutes": 0}).is_valid()


def test_worker_configuration_form_rejects_more_than_one_day():
    from tgs_admin.apps.worker_control.forms import WorkerConfigurationForm
    assert not WorkerConfigurationForm(data={"interval_minutes": 1441}).is_valid()


def test_worker_configuration_form_accepts_boundaries():
    from tgs_admin.apps.worker_control.forms import WorkerConfigurationForm
    assert WorkerConfigurationForm(data={"interval_minutes": 1}).is_valid()
    assert WorkerConfigurationForm(data={"interval_minutes": 1440}).is_valid()
