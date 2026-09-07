from django.contrib import admin
from django.urls import include, path
from src import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("admin/monitoring/", include("src.apps.monitoring.urls")),
    path("admin/worker-control/", include("src.apps.worker_control.urls")),
]

# Serve static files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
