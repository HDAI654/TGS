from channels_service.infrastructure.persistence.repositories import SQLAlchemyChannelRepository, SQLAlchemyCountryRepository


def test_channel_repository_contract_has_only_read_operations():
    methods = {name for name in dir(SQLAlchemyChannelRepository) if not name.startswith("_")}
    assert {"get_by_id", "get_all", "search", "exist"}.issubset(methods)
    assert not {"add", "update", "delete", "create"}.intersection(methods)


def test_country_repository_contract_has_only_read_operations():
    methods = {name for name in dir(SQLAlchemyCountryRepository) if not name.startswith("_")}
    assert {"get_by_id", "get_all", "search", "exist"}.issubset(methods)
    assert not {"add", "update", "delete", "create"}.intersection(methods)
