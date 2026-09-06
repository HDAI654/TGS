from django.urls import path
from .views import worker_configuration

urlpatterns = [path("", worker_configuration, name="worker_configuration")]
