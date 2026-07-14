import uuid
from src.modules.channels.domain.entities.url_entity import URLEntity
from src.modules.channels.domain.value_objects.id import ID
from src.modules.channels.domain.value_objects.url import URL


class TestURLEntity:
    def test_create_success(self):
        id = str(uuid.uuid4())
        url = "http://example.com"

        url_en = URLEntity.create(
            id=id,
            url=url,
        )

        assert isinstance(url_en.id, ID)
        assert url_en.id.value == id

        assert isinstance(url_en.url, URL)
        assert url_en.url.value == url

    def test_create_with_vos(self):
        id = ID(str(uuid.uuid4()))
        url = URL("http://example.com")

        url_en = URLEntity(
            id=id,
            url=url,
        )

        assert isinstance(url_en.id, ID)
        assert url_en.id.value == id.value

        assert isinstance(url_en.url, URL)
        assert url_en.url.value == url.value

    def test_create_without_id(self):
        url = "http://example.com"

        url_en = URLEntity.create(
            url=url,
        )

        assert isinstance(url_en.id, ID)
        assert url_en.id.value and len(url_en.id.value) == 36

        assert isinstance(url_en.url, URL)
        assert url_en.url.value == url
