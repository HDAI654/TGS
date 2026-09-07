"""In-memory implementation for country repository interface."""

from src.domain.entities.country import Country
from src.domain.ports.country_repository import CountryRepository


class InMemoryCountryRepository(CountryRepository):
    """In-memory country repository. Stores countries in a dict keyed by code."""

    def __init__(self, countries: list[Country] | None = None):
        self._countries: dict[str, Country] = {
            c.country_code: c for c in (countries or [])
        }

    async def get_by_id(self, country_code: str) -> Country | None:
        return self._countries.get(country_code)

    async def get_all(self) -> list[Country]:
        return list(self._countries.values())

    async def search(
        self, text: str, limit: int, offset: int
    ) -> tuple[list[Country], int]:
        pattern = text.lower()
        results = [
            c
            for c in self._countries.values()
            if (
                pattern in c.country_code.lower()
                or pattern in c.country_name.lower()
                or pattern in c.timezone.lower()
            )
        ]
        total = len(results)
        results.sort(key=lambda c: c.country_code.lower())
        paginated = results[offset : offset + limit]
        return paginated, total

    async def exist(self, id: str) -> bool:
        return id in self._countries
