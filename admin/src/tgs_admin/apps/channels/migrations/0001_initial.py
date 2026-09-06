import uuid
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ("categories", "0001_initial"),
        ("countries", "0001_initial"),
    ]
    operations = [
        migrations.CreateModel(
            name="Channel",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("language", models.CharField(max_length=50)),
                ("urls", models.JSONField(default=dict)),
                (
                    "category",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="channels",
                        to="categories.category",
                    ),
                ),
                (
                    "country",
                    models.ForeignKey(
                        db_column="country_code",
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="channels",
                        to="countries.country",
                        to_field="country_code",
                    ),
                ),
            ],
            options={"db_table": "channels", "ordering": ("name", "id")},
        )
    ]
