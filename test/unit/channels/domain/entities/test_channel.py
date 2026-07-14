import uuid
from src.modules.channels.domain.entities.channel import ChannelEntity
from src.modules.channels.domain.value_objects.id import ID
from src.modules.channels.domain.value_objects.name import Name
from src.modules.channels.domain.value_objects.category import Category
from src.modules.channels.domain.value_objects.language import Language
from src.modules.channels.domain.value_objects.country_code import CountryCode
from src.modules.channels.domain.value_objects.is_geo_blocked import IsGeoBlocked


class TestChannelEntity:
    def test_create_success(self):
        id = str(uuid.uuid4())
        name = "HDAI News"
        category = "News"
        language = "eng"
        country_code = "CA"
        is_geo_blocked = False

        channel = ChannelEntity.create(
            id=id,
            name=name,
            category=category,
            language=language,
            country_code=country_code,
            is_geo_blocked=is_geo_blocked,
        )

        assert isinstance(channel.id, ID)
        assert channel.id.value == id

        assert isinstance(channel.name, Name)
        assert channel.name.value == name

        assert isinstance(channel.category, Category)
        assert channel.category.value == category

        assert isinstance(channel.language, Language)
        assert channel.language.value == language

        assert isinstance(channel.country_code, CountryCode)
        assert channel.country_code.value == country_code

        assert isinstance(channel.is_geo_blocked, IsGeoBlocked)
        assert channel.is_geo_blocked.value == is_geo_blocked

    def test_create_with_vos(self):
        id = ID(str(uuid.uuid4()))
        name = Name("HDAI News")
        category = Category("News")
        language = Language("eng")
        country_code = CountryCode("CA")
        is_geo_blocked = IsGeoBlocked(False)

        channel = ChannelEntity(
            id=id,
            name=name,
            category=category,
            language=language,
            country_code=country_code,
            is_geo_blocked=is_geo_blocked,
        )

        assert isinstance(channel.id, ID)
        assert channel.id.value == id.value

        assert isinstance(channel.name, Name)
        assert channel.name.value == name.value

        assert isinstance(channel.category, Category)
        assert channel.category.value == category.value

        assert isinstance(channel.language, Language)
        assert channel.language.value == language.value

        assert isinstance(channel.country_code, CountryCode)
        assert channel.country_code.value == country_code.value

        assert isinstance(channel.is_geo_blocked, IsGeoBlocked)
        assert channel.is_geo_blocked.value == is_geo_blocked.value

    def test_create_without_id(self):
        name = "HDAI News"
        category = "News"
        language = "eng"
        country_code = "CA"
        is_geo_blocked = False

        channel = ChannelEntity.create(
            name=name,
            category=category,
            language=language,
            country_code=country_code,
            is_geo_blocked=is_geo_blocked,
        )

        assert isinstance(channel.id, ID)
        assert channel.id.value and len(channel.id.value) == 36

        assert isinstance(channel.name, Name)
        assert channel.name.value == name

        assert isinstance(channel.category, Category)
        assert channel.category.value == category

        assert isinstance(channel.language, Language)
        assert channel.language.value == language

        assert isinstance(channel.country_code, CountryCode)
        assert channel.country_code.value == country_code

        assert isinstance(channel.is_geo_blocked, IsGeoBlocked)
        assert channel.is_geo_blocked.value == is_geo_blocked
