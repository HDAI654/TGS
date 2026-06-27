import pytest
from sqlalchemy import select, exists
from src.channel_app.infrastructure.persistence.models import CountryModel
from src.core.database import engine, Base, get_async_session
from src.channel_app.infrastructure.persistence.sqlal_country_repo import (
    SQLAL_CountryRepository,
)
from src.channel_app.domain.factories.country_factory import CountryFactory
from src.channel_app.domain.value_objects.country_code import CountryCode
from src.channel_app.domain.value_objects.name import Name
from src.channel_app.domain.value_objects.timezone import Timezone
from src.channel_app.domain.value_objects.count import Count
from src.core.exceptions import (
    CountryNotFoundError,
    NoChangesError,
    InvalidFieldError,
    DatabaseOperationError,
)


class TestCountryRepo:
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
        return SQLAL_CountryRepository(db_session)

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
    async def second_country_seed(self, db_session):
        country = CountryModel(
            country_code="CA",
            country_name="Canada",
            capital="Ottawa",
            timezone="America/Toronto",
            has_channels=True,
            channel_count=5,
        )
        db_session.add(country)
        await db_session.flush()
        return country

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
    async def non_existent_country_code(self):
        return CountryCode("XX")

    async def test_add_successfully(self, repo, db_session):
        country = CountryFactory.create(
            country_code="FR",
            country_name="France",
            capital="Paris",
            timezone="Europe/Paris",
            channel_count=8,
        )

        await repo.add(country)

        result = await db_session.execute(
            select(CountryModel).where(CountryModel.country_code == "FR")
        )
        saved_country = result.scalar_one()

        assert saved_country.country_code == "FR"
        assert saved_country.country_name == "France"
        assert saved_country.capital == "Paris"
        assert saved_country.timezone == "Europe/Paris"
        assert saved_country.channel_count == 8

    async def test_get_by_code_successfully(self, repo, country_entity, country_seed):
        result = await repo.get_by_code(country_entity.country_code)

        assert result.country_code.value == country_seed.country_code
        assert result.country_name.value == country_seed.country_name
        assert result.capital.value == country_seed.capital
        assert result.timezone.value == country_seed.timezone
        assert result.channel_count.value == country_seed.channel_count

    async def test_get_by_code_not_found(self, repo, non_existent_country_code):
        with pytest.raises(CountryNotFoundError):
            await repo.get_by_code(non_existent_country_code)

    async def test_exists_by_code(self, repo, country_entity):
        assert await repo.exists_by_code(country_entity.country_code) is True
        assert await repo.exists_by_code(CountryCode("XX")) is False

    async def test_get_country_codes(self, repo, country_seed, second_country_seed):
        codes = await repo.get_country_codes()

        assert len(codes) == 2
        assert CountryCode(country_seed.country_code) in codes
        assert CountryCode(second_country_seed.country_code) in codes

    async def test_update_name_successfully(self, repo, db_session, country_entity):
        await repo.update(
            country_entity.country_code,
            new_country_name=Name("United States of America"),
        )

        result = await db_session.execute(
            select(CountryModel).where(CountryModel.country_code == "US")
        )
        updated_country = result.scalar_one()

        assert updated_country.country_name == "United States of America"
        assert updated_country.capital == "Washington D.C."  # Unchanged
        assert updated_country.timezone == "America/New_York"  # Unchanged

    async def test_update_multiple_fields_successfully(
        self, repo, db_session, country_entity
    ):
        await repo.update(
            country_entity.country_code,
            new_country_name=Name("United States of America"),
            new_capital=Name("Washington"),
            new_timezone=Timezone("America/New_York"),
            new_channel_count=Count(15),
        )

        result = await db_session.execute(
            select(CountryModel).where(CountryModel.country_code == "US")
        )
        updated_country = result.scalar_one()

        assert updated_country.country_name == "United States of America"
        assert updated_country.capital == "Washington"
        assert updated_country.timezone == "America/New_York"
        assert updated_country.channel_count == 15

    async def test_update_raises_when_no_fields_provided(self, repo, country_entity):
        with pytest.raises(NoChangesError):
            await repo.update(country_entity.country_code)

    async def test_update_raises_when_country_not_found(
        self, repo, non_existent_country_code
    ):
        with pytest.raises(CountryNotFoundError):
            await repo.update(
                non_existent_country_code, new_country_name=Name("New Name")
            )

    async def test_delete_successfully(self, repo, db_session, country_entity):
        await repo.delete(country_entity.country_code)

        result = await db_session.execute(
            select(exists().where(CountryModel.country_code == "US"))
        )
        assert result.scalar() is False

    async def test_delete_raises_when_country_not_found(
        self, repo, non_existent_country_code
    ):
        with pytest.raises(CountryNotFoundError):
            await repo.delete(non_existent_country_code)

    async def test_search_all_countries(self, repo, country_seed, second_country_seed):
        result = await repo.search(fields=[], filters={})

        assert len(result) == 2
        assert result[0]["country_code"] == "US"
        assert result[1]["country_code"] == "CA"

    async def test_search_with_field_projection(self, repo, country_seed):
        result = await repo.search(fields=["country_code", "country_name"], filters={})

        assert len(result) == 1
        assert "country_code" in result[0]
        assert "country_name" in result[0]
        assert "capital" not in result[0]
        assert "timezone" not in result[0]

    async def test_search_with_exact_filter(self, repo, country_seed):
        result = await repo.search(fields=[], filters={"country_code": "US"})

        assert len(result) == 1
        assert result[0]["country_code"] == "US"
        assert result[0]["country_name"] == "United States"

    async def test_search_with_partial_match_filter(self, repo, country_seed):
        result = await repo.search(fields=[], filters={"country_name": "United"})

        assert len(result) == 1
        assert result[0]["country_code"] == "US"

    async def test_search_with_channel_count_range(
        self, repo, country_seed, second_country_seed
    ):
        result = await repo.search(
            fields=[], filters={"channel_count": {"min": 8, "max": 15}}
        )

        assert len(result) == 1
        assert result[0]["country_code"] == "US"
        assert result[0]["channel_count"] == 10

    async def test_search_with_multiple_filters(self, repo, country_seed):
        result = await repo.search(
            fields=[],
            filters={
                "country_code": "US",
                "has_channels": True,
            },
        )

        assert len(result) == 1
        assert result[0]["country_code"] == "US"

    async def test_search_returns_empty_list_for_no_matches(self, repo):
        result = await repo.search(fields=[], filters={"country_code": "XX"})

        assert result == []

    async def test_search_raises_invalid_field_error(self, repo):
        with pytest.raises(InvalidFieldError):
            await repo.search(fields=["invalid_field"], filters={})

    async def test_search_raises_invalid_filter_error(self, repo):
        with pytest.raises(InvalidFieldError):
            await repo.search(fields=[], filters={"invalid_filter": "value"})
