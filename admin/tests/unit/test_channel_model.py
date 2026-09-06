import uuid

import pytest
from django.core.exceptions import ValidationError

pytestmark = pytest.mark.django_db


def test_channel_generates_uuid_and_preserves_uniqueness():
    from tgs_admin.apps.channels.models import Channel
    from tgs_admin.apps.categories.models import Category
    from tgs_admin.apps.countries.models import Country

    category = Category.objects.create(name="News")
    country = Country.objects.create(
        country_code="US", country_name="United States", timezone="America/New_York"
    )
    first = Channel.objects.create(
        name="A",
        category=category,
        language="en",
        country=country,
        urls={"urls": ["https://example.com"]},
    )
    second = Channel.objects.create(
        name="B",
        category=category,
        language="en",
        country=country,
        urls={"urls": ["https://example.org"]},
    )
    assert isinstance(first.id, uuid.UUID)
    assert isinstance(second.id, uuid.UUID)
    assert first.id != second.id


def test_channel_rejects_non_url_items():
    from tgs_admin.apps.channels.models import Channel
    from tgs_admin.apps.categories.models import Category
    from tgs_admin.apps.countries.models import Country

    category = Category.objects.create(name="News")
    country = Country.objects.create(
        country_code="US", country_name="United States", timezone="America/New_York"
    )
    with pytest.raises(ValidationError):
        Channel.objects.create(
            name="A",
            category=category,
            language="en",
            country=country,
            urls={"urls": ["not-a-url"]},
        )
