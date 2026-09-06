from django.contrib import admin
from .models import WorkerConfiguration


@admin.register(WorkerConfiguration)
class WorkerConfigurationAdmin(admin.ModelAdmin):
    list_display = ("id", "interval_minutes", "updated_at")
    readonly_fields = ("updated_at",)

    def has_add_permission(self, request):
        return not WorkerConfiguration.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
