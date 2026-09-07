from django.contrib import admin
from .models import Channel
from django.contrib.auth.models import User, Group


@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "category", "language", "country")
    search_fields = (
        "name",
        "language",
        "country__country_code",
        "country__country_name",
        "category__name",
    )
    list_filter = ("category", "country")
    autocomplete_fields = ("category", "country")
    readonly_fields = ("id",)


admin.site.unregister(User)
admin.site.unregister(Group)
