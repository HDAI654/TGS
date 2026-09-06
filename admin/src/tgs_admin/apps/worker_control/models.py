from django.db import models


class WorkerConfiguration(models.Model):
    interval_minutes = models.PositiveIntegerField(default=30)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "worker_configuration"

    def __str__(self) -> str:
        return f"Every {self.interval_minutes} minutes"
