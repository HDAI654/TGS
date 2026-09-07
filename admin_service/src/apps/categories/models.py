from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        db_table = "categories"
        verbose_name_plural = "Categories"
        ordering = ("id",)

    def __str__(self) -> str:
        return self.name
