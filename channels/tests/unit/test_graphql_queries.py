from uuid import uuid4

import pytest

from channels_service.domain.entities.category import Category
from channels_service.domain.entities.channel import Channel
from channels_service.domain.entities.country import Country
from channels_service.presentation.graphql.schema import channel_type, country_type


def test_channel_type_exposes_nested_category_and_urls() -> None:
    entity = Channel(
        id=uuid4(),
        name="Example",
        category=Category(id=1, name="News"),
        language="en",
        country_code="US",
        urls=("https://example.com",),
    )

    result = channel_type(entity)

    assert result.name == "Example"
    assert result.category.id == 1
    assert result.category.name == "News"
    assert result.urls == ["https://example.com"]


def test_country_type_exposes_all_country_fields() -> None:
    entity = Country(
        country_code="US",
        country_name="United States",
        timezone="America/New_York",
        has_channels=True,
        channel_count=10,
    )

    result = country_type(entity)

    assert result.country_code == "US"
    assert result.country_name == "United States"
    assert result.timezone == "America/New_York"
    assert result.has_channels is True
    assert result.channel_count == 10
