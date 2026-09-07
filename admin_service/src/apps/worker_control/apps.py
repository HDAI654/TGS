from django.apps import AppConfig


class WorkerControlConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "src.apps.worker_control"
    label = "worker_control"
