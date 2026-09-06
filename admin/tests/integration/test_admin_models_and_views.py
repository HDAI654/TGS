import uuid

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.exceptions import ValidationError

from tgs_admin.apps.categories.models import Category
from tgs_admin.apps.channels.models import Channel
from tgs_admin.apps.countries.models import Country

pytestmark = pytest.mark.django_db


def _staff_client(client):
    user = get_user_model().objects.create_superuser(
        username="admin", email="admin@example.com", password="strong-password"
    )
    assert client.login(username="admin", password="strong-password")
    return user


def test_channel_urls_must_be_a_urls_list(client):
    category = Category.objects.create(name="News")
    country = Country.objects.create(
        country_code="US", country_name="United States", timezone="America/New_York"
    )

    channel = Channel(
        name="Example",
        category=category,
        language="en",
        country=country,
        urls={"urls": [123]},
    )
    with pytest.raises(ValidationError):
        channel.full_clean()


def test_channel_uuid_is_generated_for_each_record():
    category = Category.objects.create(name="News")
    country = Country.objects.create(
        country_code="US", country_name="United States", timezone="America/New_York"
    )
    first = Channel.objects.create(
        name="First",
        category=category,
        language="en",
        country=country,
        urls={"urls": ["https://first.example"]},
    )
    second = Channel.objects.create(
        name="Second",
        category=category,
        language="en",
        country=country,
        urls={"urls": ["https://second.example"]},
    )

    assert isinstance(first.id, uuid.UUID)
    assert isinstance(second.id, uuid.UUID)
    assert first.id != second.id


def test_monitoring_pages_require_staff_authentication(client):
    response = client.get(reverse("monitoring_dashboard"))
    assert response.status_code == 302
    assert "/admin/login/" in response.url


def test_staff_can_open_monitoring_dashboard(client):
    _staff_client(client)
    response = client.get(reverse("monitoring_dashboard"))
    assert response.status_code == 200
    assert "System Dashboard" in response.content.decode()


def test_worker_configuration_requires_staff_authentication(client):
    response = client.get(reverse("worker_configuration"))
    assert response.status_code == 302
    assert "/admin/login/" in response.url


def test_channel_rejects_urls_object_without_list():
    channel = Channel(
        name="Example",
        category=Category(name="News"),
        country=Country(
            country_code="US",
            country_name="United States",
            timezone="America/New_York",
        ),
        language="en",
        urls={"urls": "https://example.com"},
    )
    with pytest.raises(ValidationError):
        channel.full_clean()


def test_channel_rejects_non_string_url_items():
    channel = Channel(
        name="Example",
        category=Category(name="News"),
        country=Country(
            country_code="US",
            country_name="United States",
            timezone="America/New_York",
        ),
        language="en",
        urls={"urls": [123]},
    )
    with pytest.raises(ValidationError):
        channel.full_clean()


def test_worker_health_requires_exactly_one_worker():
    from unittest.mock import patch

    from tgs_admin.apps.monitoring.services import worker_status

    class Inspector:
        def active(self):
            return {"worker-a": []}

        def registered(self):
            return {"worker-a": ["task"]}

    with patch(
        "tgs_admin.apps.monitoring.services.app.control.inspect",
        return_value=Inspector(),
    ):
        result = worker_status()

    assert result["count"] == 1
    assert result["expected_count"] == 1
    assert result["status"] == "healthy"
