from django.db import models


class Country(models.Model):
    country_code = models.CharField(max_length=2, primary_key=True)
    country_name = models.CharField(max_length=100)
    timezone = models.CharField(max_length=100)
    has_channels = models.BooleanField(default=False)
    channel_count = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "countries"
        ordering = ("country_code",)
        verbose_name_plural = "Countries"

    def __str__(self) -> str:
        return f"{self.country_code} - {self.country_name}"
