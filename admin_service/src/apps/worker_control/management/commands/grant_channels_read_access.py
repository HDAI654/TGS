import os

from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = "Grant the configured Channels database role read-only access."

    def handle(self, *args, **options):
        channels_user = os.getenv("CHANNELS_DB_USER", "tgs_channels")
        with connection.cursor() as cursor:
            cursor.execute(
                "GRANT USAGE ON SCHEMA public TO %s"
                % connection.ops.quote_name(channels_user)
            )
            for table in ("categories", "countries", "channels"):
                quoted_table = connection.ops.quote_name(table)
                quoted_user = connection.ops.quote_name(channels_user)
                cursor.execute(
                    "REVOKE ALL PRIVILEGES ON TABLE %s FROM %s"
                    % (quoted_table, quoted_user)
                )
                cursor.execute(
                    "GRANT SELECT ON TABLE %s TO %s" % (quoted_table, quoted_user)
                )
        self.stdout.write(
            self.style.SUCCESS(
                f"Channels read-only permissions are ready for {channels_user}."
            )
        )
