from django.contrib import admin
from .models import Country


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ("country_code", "country_name", "timezone", "has_channels", "channel_count")
    search_fields = ("country_code", "country_name", "timezone")
    list_filter = ("has_channels",)
    ordering = ("country_code",)
