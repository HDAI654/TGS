from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("admin/monitoring/", include("tgs_admin.apps.monitoring.urls")),
    path("admin/worker-control/", include("tgs_admin.apps.worker_control.urls")),
]
