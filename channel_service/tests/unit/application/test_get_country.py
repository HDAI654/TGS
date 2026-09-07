import pytest
from src.application.queries import get_country


@pytest.mark.asyncio
async def test_get_country_found(mock_country_repo, sample_country):
    country_code = sample_country.country_code
    mock_country_repo.get_by_id_return = sample_country

    result = await get_country(mock_country_repo, country_code)

    assert result == sample_country
    assert mock_country_repo.get_by_id_called_with == country_code


@pytest.mark.asyncio
async def test_get_country_not_found(mock_country_repo):
    country_code = "XX"
    mock_country_repo.get_by_id_return = None

    result = await get_country(mock_country_repo, country_code)

    assert result is None
    assert mock_country_repo.get_by_id_called_with == country_code


@pytest.mark.asyncio
async def test_get_country_repository_raises(mock_country_repo):
    country_code = "US"

    async def raise_exception(*args, **kwargs):
        raise ValueError("Invalid code")

    mock_country_repo.get_by_id = raise_exception

    with pytest.raises(ValueError, match="Invalid code"):
        await get_country(mock_country_repo, country_code)
