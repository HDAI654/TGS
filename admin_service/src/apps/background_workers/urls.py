from django.urls import path

from . import views

urlpatterns = [
    path(
        "",
        views.dashboard,
        name="background_worker_dashboard",
    ),
    path(
        "status/",
        views.status,
        name="background_worker_status",
    ),
    path(
        "start/",
        views.start,
        name="background_worker_start",
    ),
    path(
        "stop/",
        views.stop,
        name="background_worker_stop",
    ),
    path(
        "restart/",
        views.restart,
        name="background_worker_restart",
    ),
]
