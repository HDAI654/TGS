from django.core.management.base import BaseCommand
from tgs_admin.apps.worker_control.services import ensure_schedule


class Command(BaseCommand):
    help = "Ensure the single update_data periodic schedule exists."

    def handle(self, *args, **options):
        ensure_schedule()
        self.stdout.write(self.style.SUCCESS("Worker schedule is ready."))
