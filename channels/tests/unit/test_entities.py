from uuid import uuid4
import pytest
from channels_service.domain.entities.category import Category
from channels_service.domain.entities.channel import Channel
from channels_service.domain.entities.country import Country


def test_country_is_immutable_and_serializable():
    country = Country("IR", "Iran", "Asia/Tehran", True, 3)
    assert country.to_dict() == {
        "country_code": "IR", "country_name": "Iran", "timezone": "Asia/Tehran",
        "has_channels": True, "channel_count": 3,
    }
    with pytest.raises(AttributeError):
        country.country_name = "Changed"


def test_channel_contains_nested_category_and_urls():
    channel = Channel(
        uuid4(), "News", Category(1, "News"), "en", "US",
        ("https://example.com",),
    )
    assert channel.category.name == "News"
    assert channel.to_dict()["urls"] == ["https://example.com"]
