from channels_service.domain.entities.country import Country
from channels_service.domain.ports.country_repository import CountryRepository


async def get_country(
    repository: CountryRepository, country_code: str
) -> Country | None:
    return await repository.get_by_id(country_code)


async def search_countries(
    repository: CountryRepository,
    text: str | None,
    limit: int,
    offset: int,
) -> tuple[list[Country], int] | None:
    if text is None or not text.strip():
        return None
    return await repository.search(text, limit, offset)
