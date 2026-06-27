from abc import ABC, abstractmethod
from typing import Any
from src.channel_app.domain.entities.country import CountryEntity
from src.core.id_vo import ID
from src.channel_app.domain.value_objects.country_code import CountryCode
from src.channel_app.domain.value_objects.name import Name
from src.channel_app.domain.value_objects.timezone import Timezone
from src.channel_app.domain.value_objects.has_channels import HasChannels
from src.channel_app.domain.value_objects.count import Count


class ICountryRepository(ABC):
    """Repository interface for Country entities."""

    @abstractmethod
    async def add(self, country: CountryEntity) -> None:
        """Create a new country in the database."""
        pass

    @abstractmethod
    async def update(
        self,
        country_code: CountryCode,
        new_country_name: Name | None = None,
        new_capital: Name | None = None,
        new_timezone: Timezone | None = None,
        new_channel_count: Count | None = None,
    ) -> None:
        """Update an existing country in the database."""
        pass

    @abstractmethod
    async def delete(self, country_code: CountryCode) -> None:
        """Delete a country by CountryCode."""
        pass

    @abstractmethod
    async def get_by_code(self, country_code: CountryCode) -> CountryEntity:
        """Get a country by CountryCode."""
        pass

    @abstractmethod
    async def get_country_codes(self) -> list[CountryCode]:
        """Get all CountryCodes of countries"""
        pass

    @abstractmethod
    async def search(
        self, fields: list[str], filters: dict[str, Any]
    ) -> list[CountryEntity]:
        """Search countries by filters and return specified fields."""
        pass

    @abstractmethod
    async def exists_by_id(self, country_code: CountryCode) -> bool:
        """Check if a country exists by CountryCode."""
        pass

    @abstractmethod
    async def upsert_batch(self, countries: list[CountryEntity]) -> None:
        """Add new countries and update changed countries"""
        pass
