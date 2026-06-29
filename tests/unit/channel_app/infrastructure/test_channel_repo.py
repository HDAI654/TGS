import pytest
from sqlalchemy import select, exists
from src.channel_app.infrastructure.persistence.models import ChannelModel, URLModel
from src.core.database import engine, Base, get_async_session
from src.channel_app.infrastructure.persistence.sqlal_channel_repo import (
    SQLAL_ChannelRepository,
)
from shared.domain.factories.channel_factory import ChannelFactory
from shared.domain.factories.url_factory import URLFactory
from shared.domain.value_objects.country_code import CountryCode
from shared.domain.value_objects.name import Name
from shared.domain.value_objects.category import Category
from shared.domain.value_objects.is_geo_blocked import IsGeoBlocked
from src.core.id_vo import ID
from src.core.exceptions import (
    ChannelNotFoundError,
    ChannelDuplicateError,
    URLDuplicateError,
    NoChangesError,
    InvalidFieldError,
    URLNotFoundError,
)


class TestChannelRepo:
    @pytest.fixture(autouse=True)
    async def setup_db(self):
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        yield
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    @pytest.fixture
    async def db_session(self):
        async for session in get_async_session():
            yield session
            await session.rollback()
            break

    @pytest.fixture
    async def repo(self, db_session):
        return SQLAL_ChannelRepository(db_session)

    @pytest.fixture
    async def channel_seed(self, db_session):
        channel = ChannelModel(
            nano_id="diede23e6cdd5e",
            name="CNN",
            category="News",
            language="eng",
            country_code="US",
            is_geo_blocked=False,
        )
        db_session.add(channel)
        await db_session.flush()
        return channel

    @pytest.fixture
    async def second_channel_seed(self, db_session):
        channel = ChannelModel(
            nano_id="edeii9e5qw5d5e",
            name="BBC",
            category="News",
            language="eng",
            country_code="UK",
            is_geo_blocked=False,
        )
        db_session.add(channel)
        await db_session.flush()
        return channel

    @pytest.fixture
    async def url_seed(self, db_session, channel_seed):
        url = URLModel(
            nano_id="eqq9e0mkoesp45",
            channel_id=channel_seed.nano_id,
            url="https://edition.cnn.com",
        )
        db_session.add(url)
        await db_session.flush()
        return url

    @pytest.fixture
    async def channel_entity(self, channel_seed):
        return ChannelFactory.create(
            id=channel_seed.nano_id,
            name=channel_seed.name,
            category=channel_seed.category,
            language=channel_seed.language,
            country_code=channel_seed.country_code,
            is_geo_blocked=channel_seed.is_geo_blocked,
        )

    @pytest.fixture
    async def non_existent_channel_id(self):
        return ID("wwwodcx525w2w0")

    @pytest.fixture
    async def non_existent_url_id(self):
        return ID("eciej52wd5w020")

    async def test_add_successfully(self, repo, db_session):
        channel_id = ID("ewd000fvrlknis")
        channel = ChannelFactory.create(
            id=channel_id.value,
            name="Fox News",
            category="News",
            language="eng",
            country_code="US",
            is_geo_blocked=False,
        )

        await repo.add(channel)

        result = await db_session.execute(
            select(ChannelModel).where(ChannelModel.nano_id == channel_id.value)
        )
        saved_channel = result.scalar_one()

        assert saved_channel.nano_id == channel_id.value
        assert saved_channel.name == "Fox News"
        assert saved_channel.category == "News"
        assert saved_channel.language == "eng"
        assert saved_channel.country_code == "US"
        assert saved_channel.is_geo_blocked is False

    async def test_add_duplicate(self, repo):
        channel_id = ID("ewd000fvrlknis")
        channel = ChannelFactory.create(
            id=channel_id.value,
            name="Fox News",
            category="News",
            language="eng",
            country_code="US",
            is_geo_blocked=False,
        )

        await repo.add(channel)

        with pytest.raises(ChannelDuplicateError):
            await repo.add(channel)

    async def test_get_by_id_successfully(self, repo, channel_entity, channel_seed):
        result = await repo.get_by_id(channel_entity.id)

        assert result.id.value == channel_seed.nano_id
        assert result.name.value == channel_seed.name
        assert result.category.value == channel_seed.category
        assert result.language.value == channel_seed.language
        assert result.country_code.value == channel_seed.country_code
        assert result.is_geo_blocked.value == channel_seed.is_geo_blocked

    async def test_get_by_id_not_found(self, repo, non_existent_channel_id):
        with pytest.raises(ChannelNotFoundError):
            await repo.get_by_id(non_existent_channel_id)

    async def test_exists_by_id(self, repo, channel_entity):
        assert await repo.exists_by_id(channel_entity.id) is True
        assert await repo.exists_by_id(ID("ecddinwkje252c")) is False

    async def test_update_name_successfully(self, repo, db_session, channel_entity):
        await repo.update(
            channel_entity.id,
            new_name=Name("CNN International"),
        )

        result = await db_session.execute(
            select(ChannelModel).where(ChannelModel.nano_id == channel_entity.id.value)
        )
        updated_channel = result.scalar_one()

        assert updated_channel.name == "CNN International"
        assert updated_channel.category == "News"  # Unchanged
        assert updated_channel.country_code == "US"  # Unchanged

    async def test_update_multiple_fields_successfully(
        self, repo, db_session, channel_entity
    ):
        await repo.update(
            channel_entity.id,
            new_name=Name("CNN International"),
            new_category=Category("Entertainment"),
            new_country_code=CountryCode("UK"),
            new_is_geo_blocked=IsGeoBlocked(True),
        )

        result = await db_session.execute(
            select(ChannelModel).where(ChannelModel.nano_id == channel_entity.id.value)
        )
        updated_channel = result.scalar_one()

        assert updated_channel.name == "CNN International"
        assert updated_channel.category == "Entertainment"
        assert updated_channel.country_code == "UK"
        assert updated_channel.is_geo_blocked is True

    async def test_update_raises_when_no_fields_provided(self, repo, channel_entity):
        with pytest.raises(NoChangesError):
            await repo.update(channel_entity.id)

    async def test_update_raises_when_channel_not_found(
        self, repo, non_existent_channel_id
    ):
        with pytest.raises(ChannelNotFoundError):
            await repo.update(non_existent_channel_id, new_name=Name("New Name"))

    async def test_delete_successfully(self, repo, db_session, channel_entity):
        await repo.delete(channel_entity.id)

        result = await db_session.execute(
            select(exists().where(ChannelModel.nano_id == channel_entity.id.value))
        )
        assert result.scalar() is False

    async def test_delete_raises_when_channel_not_found(
        self, repo, non_existent_channel_id
    ):
        with pytest.raises(ChannelNotFoundError):
            await repo.delete(non_existent_channel_id)

    async def test_search_all_channels(self, repo, channel_seed, second_channel_seed):
        result = await repo.search(filters={})

        assert len(result) == 2
        ids = {c.id.value for c in result}
        assert channel_seed.nano_id in ids
        assert second_channel_seed.nano_id in ids

    async def test_search_with_exact_filter(self, repo, channel_seed):
        result = await repo.search(filters={"country_code": "US"})

        assert len(result) == 1
        assert result[0].id.value == channel_seed.nano_id
        assert result[0].name.value == "CNN"

    async def test_search_with_partial_match_filter(self, repo, channel_seed):
        result = await repo.search(filters={"name": "CN"})

        assert len(result) == 1
        assert result[0].id.value == channel_seed.nano_id
        assert result[0].name.value == "CNN"

    async def test_search_with_id_filter(self, repo, channel_seed):
        result = await repo.search(filters={"id": channel_seed.nano_id})

        assert len(result) == 1
        assert result[0].id.value == channel_seed.nano_id

    async def test_search_with_language_filter(self, repo, channel_seed):
        result = await repo.search(filters={"language": "eng"})

        assert len(result) == 1
        assert result[0].id.value == channel_seed.nano_id

    async def test_search_with_geo_blocked_filter(self, repo, channel_seed):
        result = await repo.search(filters={"is_geo_blocked": False})

        assert len(result) == 1
        assert result[0].id.value == channel_seed.nano_id

    async def test_search_with_multiple_filters(self, repo, channel_seed):
        result = await repo.search(
            filters={
                "country_code": "US",
                "category": "News",
            },
        )

        assert len(result) == 1
        assert result[0].id.value == channel_seed.nano_id

    async def test_search_returns_empty_list_for_no_matches(self, repo):
        result = await repo.search(filters={"country_code": "XX"})

        assert result == []

    async def test_search_raises_invalid_filter_error(self, repo):
        with pytest.raises(InvalidFieldError):
            await repo.search(filters={"invalid_filter": "value"})

    async def test_add_new_url_successfully(self, repo, db_session, channel_entity):
        url = URLFactory.create(
            url="https://www.bbc.com",
        )

        await repo.add_new_url(channel_entity.id, url)

        result = await db_session.execute(
            select(URLModel).where(URLModel.nano_id == url.id.value)
        )
        saved_url = result.scalar_one()

        assert saved_url.nano_id == url.id.value
        assert saved_url.channel_id == channel_entity.id.value
        assert saved_url.url == "https://www.bbc.com"

    async def test_add_new_url_duplicate(self, repo, db_session, channel_entity):
        url = URLFactory.create(
            url="https://www.bbc.com",
        )

        await repo.add_new_url(channel_entity.id, url)

        with pytest.raises(URLDuplicateError):
            await repo.add_new_url(channel_entity.id, url)

    async def test_add_new_url_multiple_urls(self, repo, db_session, channel_entity):
        url1 = URLFactory.create(url="https://www.cnn.com")
        url2 = URLFactory.create(url="https://edition.cnn.com")

        await repo.add_new_url(channel_entity.id, url1)
        await repo.add_new_url(channel_entity.id, url2)

        result = await db_session.execute(
            select(URLModel).where(URLModel.channel_id == channel_entity.id.value)
        )
        urls = result.scalars().all()

        assert len(urls) == 2
        url_strings = {u.url for u in urls}
        assert "https://www.cnn.com" in url_strings
        assert "https://edition.cnn.com" in url_strings

    async def test_remove_url_successfully(self, repo, db_session, url_seed):
        await repo.remove_url(ID(url_seed.nano_id))

        result = await db_session.execute(
            select(exists().where(URLModel.nano_id == url_seed.nano_id))
        )
        assert result.scalar() is False

    async def test_remove_url_raises_when_not_found(self, repo, non_existent_url_id):
        with pytest.raises(URLNotFoundError):
            await repo.remove_url(non_existent_url_id)

    async def test_get_urls_successfully(self, repo, channel_entity, url_seed):
        result = await repo.get_urls(channel_entity.id)

        assert len(result) == 1
        assert result[0].id.value == url_seed.nano_id
        assert result[0].url.value == url_seed.url

    async def test_get_urls_multiple_urls(self, repo, db_session, channel_entity):
        url1 = URLModel(
            nano_id="ecinedwc5623ew",
            channel_id=channel_entity.id.value,
            url="https://www.cnn.com",
        )
        url2 = URLModel(
            nano_id="wsknj458ecjmmm",
            channel_id=channel_entity.id.value,
            url="https://edition.cnn.com",
        )
        db_session.add_all([url1, url2])
        await db_session.flush()

        result = await repo.get_urls(channel_entity.id)

        assert len(result) == 2
        urls = {u.url.value for u in result}
        assert "https://www.cnn.com" in urls
        assert "https://edition.cnn.com" in urls

    async def test_get_urls_returns_empty_list_for_no_urls(self, repo, channel_entity):
        result = await repo.get_urls(channel_entity.id)

        assert result == []

    async def test_get_urls_raises_for_non_existent_channel(
        self, repo, non_existent_channel_id
    ):
        result = await repo.get_urls(non_existent_channel_id)

        assert result == []
