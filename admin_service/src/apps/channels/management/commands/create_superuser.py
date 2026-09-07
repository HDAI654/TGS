import os
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create the initial superuser from environment variables."

    def handle(self, *args, **options):
        username = os.getenv("SUPER_USERNAME")
        password = os.getenv("SUPER_PASSWORD")

        if not username or not password:
            self.stdout.write(
                self.style.WARNING(
                    "SUPER_USERNAME or SUPER_PASSWORD is not set. "
                    "Skipping superuser creation."
                )
            )
            return

        User = get_user_model()

        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(f"Superuser '{username}' already exists. Skipping.")
            )
            return

        User.objects.create_superuser(
            username=username,
            password=password,
        )

        self.stdout.write(
            self.style.SUCCESS(f"Superuser '{username}' created successfully.")
        )
