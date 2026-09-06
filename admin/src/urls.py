from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("admin/monitoring/", include("src.apps.monitoring.urls")),
    path("admin/worker-control/", include("src.apps.worker_control.urls")),
]
