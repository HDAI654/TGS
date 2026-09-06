from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name="WorkerConfiguration",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("interval_minutes", models.PositiveIntegerField(default=30)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"db_table": "worker_configuration"},
        )
    ]
