import pytest
from sqlalchemy import select
from shared.models import CountryModel, ChannelModel, URLModel
from workers.core.database import engine, get_async_session
from shared.models import Base
from workers.imp.sqlal_repo import SQLAL_Repo
from shared.domain.factories.country_factory import CountryFactory
from shared.domain.factories.channel_factory import ChannelFactory
from shared.domain.factories.url_factory import URLFactory
from shared.domain.id_vo import ID
from workers.core.exceptions import DatabaseOperationError


class TestSQLALRepo:
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
        return SQLAL_Repo(db_session)

    @pytest.fixture
    async def country_seed(self, db_session):
        country = CountryModel(
            country_code="US",
            country_name="United States",
            capital="Washington D.C.",
            timezone="America/New_York",
            has_channels=True,
            channel_count=10,
        )
        db_session.add(country)
        await db_session.flush()
        return country

    @pytest.fixture
    async def channel_seed(self, db_session, country_seed):
        channel = ChannelModel(
            nano_id=ID().value,
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
    async def url_seed(self, db_session, channel_seed):
        url = URLModel(
            nano_id=ID().value,
            channel_id=channel_seed.nano_id,
            url="https://edition.cnn.com",
        )
        db_session.add(url)
        await db_session.flush()
        return url

    @pytest.fixture
    async def country_entity(self, country_seed):
        return CountryFactory.create(
            country_code=country_seed.country_code,
            country_name=country_seed.country_name,
            capital=country_seed.capital,
            timezone=country_seed.timezone,
            channel_count=country_seed.channel_count,
        )

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

    # ========== UPSERT BATCH COUNTRIES ==========

    async def test_upsert_batch_countries_inserts_new_countries(self, repo, db_session):
        countries = [
            CountryFactory.create(
                country_code="FR",
                country_name="France",
                capital="Paris",
                timezone="Europe/Paris",
                channel_count=8,
            ),
            CountryFactory.create(
                country_code="DE",
                country_name="Germany",
                capital="Berlin",
                timezone="Europe/Berlin",
                channel_count=12,
            ),
        ]

        await repo.upsert_batch_countries(countries)

        result = await db_session.execute(select(CountryModel))
        saved_countries = result.scalars().all()

        assert len(saved_countries) == 2
        codes = {c.country_code for c in saved_countries}
        assert "FR" in codes
        assert "DE" in codes

    async def test_upsert_batch_countries_updates_existing_countries(
        self, repo, db_session, country_seed
    ):
        country = CountryFactory.create(
            country_code="US",
            country_name="United States of America",
            capital="Washington",
            timezone="America/New_York",
            channel_count=20,
        )

        await repo.upsert_batch_countries([country])

        result = await db_session.execute(
            select(CountryModel).where(CountryModel.country_code == "US")
        )
        saved_country = result.scalar_one()

        assert saved_country.country_name == "United States of America"
        assert saved_country.capital == "Washington"
        assert saved_country.channel_count == 20

    async def test_upsert_batch_countries_handles_empty_list(self, repo):
        await repo.upsert_batch_countries([])
        # Should not raise any error

    # ========== UPSERT BATCH CHANNELS ==========

    async def test_upsert_batch_channels_inserts_new_channels(
        self, repo, db_session, country_seed
    ):
        channels = [
            ChannelFactory.create(
                id=ID().value,
                name="BBC News",
                category="News",
                language="eng",
                country_code="US",
                is_geo_blocked=False,
            ),
            ChannelFactory.create(
                id=ID().value,
                name="France 24",
                category="News",
                language="eng",
                country_code="US",
                is_geo_blocked=False,
            ),
        ]

        await repo.upsert_batch_channels(channels)

        result = await db_session.execute(select(ChannelModel))
        saved_channels = result.scalars().all()

        assert len(saved_channels) == 2
        names = {c.name for c in saved_channels}
        assert "BBC News" in names
        assert "France 24" in names

    async def test_upsert_batch_channels_updates_existing_channels(
        self, repo, db_session, channel_seed
    ):
        channel = ChannelFactory.create(
            id=channel_seed.nano_id,
            name="CNN International",
            category="Entertainment",
            language="eng",
            country_code="US",
            is_geo_blocked=True,
        )

        await repo.upsert_batch_channels([channel])

        result = await db_session.execute(
            select(ChannelModel).where(ChannelModel.nano_id == channel_seed.nano_id)
        )
        saved_channel = result.scalar_one()

        assert saved_channel.name == "CNN International"
        assert saved_channel.category == "Entertainment"
        assert saved_channel.is_geo_blocked is True

    async def test_upsert_batch_channels_handles_empty_list(self, repo):
        await repo.upsert_batch_channels([])
        # Should not raise any error

    async def test_upsert_batch_channels_foreign_key_error(self, repo, db_session):
        channel = ChannelFactory.create(
            id=ID().value,
            name="Invalid Channel",
            category="News",
            language="eng",
            country_code="XX",  # Non-existent country
            is_geo_blocked=False,
        )

        with pytest.raises(DatabaseOperationError):
            await repo.upsert_batch_channels([channel])

    # ========== UPSERT BATCH URLS ==========
    async def test_upsert_batch_urls_inserts_new_urls(
        self, repo, db_session, channel_seed
    ):
        url_entities = [
            (
                ID(channel_seed.nano_id),
                URLFactory.create(url="https://www.cnn.com"),
            ),
            (
                ID(channel_seed.nano_id),
                URLFactory.create(url="https://edition.cnn.com"),
            ),
        ]

        await repo.upsert_batch_urls(url_entities)

        result = await db_session.execute(
            select(URLModel).where(URLModel.channel_id == channel_seed.nano_id)
        )
        saved_urls = result.scalars().all()

        assert len(saved_urls) == 2
        urls = {u.url for u in saved_urls}
        assert "https://www.cnn.com" in urls
        assert "https://edition.cnn.com" in urls

    async def test_upsert_batch_urls_updates_existing_urls(
        self, repo, db_session, url_seed
    ):
        url_entity = (
            ID(url_seed.channel_id),
            URLFactory.create(url="https://updated.cnn.com"),
        )

        await repo.upsert_batch_urls([url_entity])

        result = await db_session.execute(
            select(URLModel).where(URLModel.nano_id == url_seed.nano_id)
        )
        saved_url = result.scalar_one()

        assert saved_url.url == "https://updated.cnn.com"

    async def test_upsert_batch_urls_handles_empty_list(self, repo):
        await repo.upsert_batch_urls([])
        # Should not raise any error

    async def test_upsert_batch_urls_foreign_key_error(self, repo, db_session):
        url_entity = (
            ID("non-existent-channel"),
            URLFactory.create(url="https://invalid.com"),
        )

        with pytest.raises(DatabaseOperationError):
            await repo.upsert_batch_urls([url_entity])

    # ========== INTEGRATION TESTS ==========
    async def test_upsert_batch_all_entities(self, repo, db_session, country_seed):
        # Create country
        country = CountryFactory.create(
            country_code="UK",
            country_name="United Kingdom",
            capital="London",
            timezone="Europe/London",
            channel_count=5,
        )

        # Create channel
        channel = ChannelFactory.create(
            id=ID().value,
            name="BBC World",
            category="News",
            language="eng",
            country_code="UK",
            is_geo_blocked=False,
        )

        # Create URL
        url_entities = [
            (channel.id, URLFactory.create(url="https://www.bbc.com")),
        ]

        # Upsert all
        await repo.upsert_batch_countries([country])
        await repo.upsert_batch_channels([channel])
        await repo.upsert_batch_urls(url_entities)

        # Verify all were inserted
        country_result = await db_session.execute(
            select(CountryModel).where(CountryModel.country_code == "UK")
        )
        assert country_result.scalar_one() is not None

        channel_result = await db_session.execute(
            select(ChannelModel).where(ChannelModel.nano_id == channel.id.value)
        )
        assert channel_result.scalar_one() is not None

        url_result = await db_session.execute(
            select(URLModel).where(URLModel.channel_id == channel.id.value)
        )
        assert len(url_result.scalars().all()) == 1
