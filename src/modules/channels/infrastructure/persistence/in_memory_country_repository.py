import logging
from typing import Tuple, Dict

from src.modules.channels.domain.entities.country import Country
from src.modules.channels.domain.ports.country_repo_interface import CountryRepository
from src.modules.channels.domain.exceptions import CountryNotFoundError

logger = logging.getLogger(__name__)


class InMemoryCountryRepository(CountryRepository):
    """
    In‑memory implementation of CountryRepository for testing/development.
    Stores countries by country_code.
    """

    def __init__(self, initial_data: Dict[str, Country] = None) -> None:
        self._storage: Dict[str, Country] = initial_data.copy() if initial_data else {}

    async def get_by_code(self, country_code: str) -> Country:
        logger.debug("InMemory: get_by_code(%s)", country_code)
        country = self._storage.get(country_code)
        if country is None:
            raise CountryNotFoundError(f"Country with code {country_code} not found")
        return country

    async def get_all_country_codes(self) -> Tuple[Country, ...]:
        logger.debug("InMemory: get_all_country_codes")
        return tuple(self._storage.values())

    async def search(self, text: str, limit: int, offset: int) -> Tuple[Country, ...]:
        logger.debug("InMemory: search(text='%s', limit=%d, offset=%d)", text, limit, offset)
        if not text:
            all_items = list(self._storage.values())
        else:
            lower_text = text.lower()
            all_items = [
                cnt for cnt in self._storage.values()
                if (lower_text in cnt.country_name.lower() or
                    lower_text in cnt.country_code.lower())
            ]
        paginated = all_items[offset:offset + limit]
        return tuple(paginated)

    async def exists_by_code(self, country_code: str) -> bool:
        logger.debug("InMemory: exists_by_code(%s)", country_code)
        return country_code in self._storage

    # Helper methods for tests
    def add(self, country: Country) -> None:
        """Add or update a country in the repository."""
        self._storage[country.country_code] = country

    def clear(self) -> None:
        """Clear all data."""
        self._storage.clear()