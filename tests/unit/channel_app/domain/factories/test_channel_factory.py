import pytest
from src.channel_app.domain.factories.channel_factory import ChannelFactory


class TestChannelFactory:
    def test_create_success(self):
        channel = ChannelFactory.create(
            id="MyIDDDDDDDDDDD",
            name="Channel1",
            category="Sports",
            stream_urls=["https://example.com"],
            youtube_urls=["https://example.com"],
            languages=["eng"],
            country_id="MyIDDDDDDDDDDD",
            is_geo_blocked=True,
        )

        assert channel.id.value == "MyIDDDDDDDDDDD"
        assert channel.name.value == "Channel1"
        assert channel.stream_urls[0].value == "https://example.com"
        assert channel.youtube_urls[0].value == "https://example.com"
        assert channel.languages[0].value == "eng"
        assert channel.is_geo_blocked.value == True

    def test_create_with_non_id(self):
        channel = ChannelFactory.create(
            id="MyIDDDDDDDDDDD",
            name="Channel1",
            category="Sports",
            stream_urls=["https://example.com"],
            youtube_urls=["https://example.com"],
            languages=["eng"],
            country_id="MyIDDDDDDDDDDD",
            is_geo_blocked=True,
        )

        assert isinstance(channel.id.value, str) and len(channel.id.value) == 14

    def test_create_with_empty_language(self):
        with pytest.raises(ValueError):
            ChannelFactory.create(
                id="MyIDDDDDDDDDDD",
                name="Channel1",
                category="Sports",
                stream_urls=["https://example.com"],
                youtube_urls=["https://example.com"],
                languages=[],
                country_id="MyIDDDDDDDDDDD",
                is_geo_blocked=True,
            )

    def test_create_with_empty_url(self):
        with pytest.raises(ValueError):
            ChannelFactory.create(
                id="MyIDDDDDDDDDDD",
                name="Channel1",
                category="Sports",
                stream_urls=[],
                youtube_urls=[],
                languages=[],
                country_id="MyIDDDDDDDDDDD",
                is_geo_blocked=True,
            )
