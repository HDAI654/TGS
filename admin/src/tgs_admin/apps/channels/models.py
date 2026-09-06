import uuid
from django.core.exceptions import ValidationError
from django.db import models
from django.core.validators import URLValidator
from tgs_admin.apps.categories.models import Category
from tgs_admin.apps.countries.models import Country


def default_urls() -> dict[str, list[str]]:
    return {"urls": []}


class Channel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="channels"
    )
    language = models.CharField(max_length=50)
    country = models.ForeignKey(
        Country,
        on_delete=models.PROTECT,
        db_column="country_code",
        to_field="country_code",
        related_name="channels",
    )
    urls = models.JSONField(default=default_urls)

    class Meta:
        db_table = "channels"
        ordering = ("name", "id")

    def clean(self) -> None:
        super().clean()
        if not isinstance(self.urls, dict) or not isinstance(
            self.urls.get("urls"), list
        ):
            raise ValidationError(
                {"urls": "Expected an object containing a urls list."}
            )
        validator = URLValidator()
        errors = []
        for value in self.urls["urls"]:
            if not isinstance(value, str):
                errors.append("Every URL must be a string.")
                continue
            try:
                validator(value)
            except ValidationError:
                errors.append(f"Invalid URL: {value}")
        if errors:
            raise ValidationError({"urls": errors})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name
