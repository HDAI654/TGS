from django.urls import path
from .views import channels, dashboard, logs

urlpatterns = [
    path("", dashboard, name="monitoring_dashboard"),
    path("channels/", channels, name="monitoring_channels"),
    path("logs/", logs, name="monitoring_logs"),
]
