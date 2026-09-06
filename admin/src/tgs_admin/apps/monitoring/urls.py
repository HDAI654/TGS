from django.urls import path
from .views import channels, dashboard, logs, workers

urlpatterns = [
    path("", dashboard, name="monitoring_dashboard"),
    path("channels/", channels, name="monitoring_channels"),
    path("workers/", workers, name="monitoring_workers"),
    path("logs/", logs, name="monitoring_logs"),
]
