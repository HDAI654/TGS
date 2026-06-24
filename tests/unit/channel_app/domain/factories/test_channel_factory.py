import pytest
from src.channel_app.domain.factories.channel_factory import ChannelFactory


class TestChannelFactory:
    def test_create_success(self):
        channel = ChannelFactory.create(
            id="MyIDDDDDDDDDDD",
            name="Channel1",
            category="Sports",
            language="eng",
            country_code="US",
            is_geo_blocked=True,
        )

        assert channel.id.value == "MyIDDDDDDDDDDD"
        assert channel.name.value == "Channel1"
        assert channel.language.value == "eng"
        assert channel.category.value == "Sports"
        assert channel.is_geo_blocked.value == True

    def test_create_with_non_id(self):
        channel = ChannelFactory.create(
            name="Channel1",
            category="Sports",
            language="eng",
            country_code="US",
            is_geo_blocked=True,
        )

        assert isinstance(channel.id.value, str) and len(channel.id.value) == 14
