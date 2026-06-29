from shared.domain.factories.url_factory import URLFactory


class TestChannelFactory:
    def test_create_success(self):
        url = URLFactory.create(
            id="MyIDDDDDDDDDDD",
            url="https://example.com",
        )

        assert url.id.value == "MyIDDDDDDDDDDD"
        assert url.url.value == "https://example.com"

    def test_create_with_non_id(self):
        url = URLFactory.create(
            url="https://example.com",
        )

        assert isinstance(url.id.value, str) and len(url.id.value) == 14
