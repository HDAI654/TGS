from abc import ABC, abstractmethod
from src.modules.channels.domain.entities.country import Country


class CountryRepository(ABC):
    """Repository interface for Country entities."""

    @abstractmethod
    async def get_by_code(self, country_code: str) -> Country:
        """Get a country by CountryCode.

        Raises:
            DatabaseConnectionError: Raised when cannot connect to database.
            DatabaseTimeoutError: Raised when database operation times out.
            DatabaseOperationError: Raised when database operation fails.
            CountryNotFoundError: Raised when Country not found.
        """
        pass

    @abstractmethod
    async def get_all_country_codes(self) -> tuple[Country, ...]:
        """Get all CountryCodes of countries

        Raises:
            DatabaseConnectionError: Raised when cannot connect to database.
            DatabaseTimeoutError: Raised when database operation times out.
            DatabaseOperationError: Raised when database operation fails.
        """
        pass

    @abstractmethod
    async def search(self, text, limit, offset) -> tuple[Country, ...]:
        """Search countries.

        Raises:
            DatabaseConnectionError: Raised when cannot connect to database.
            DatabaseTimeoutError: Raised when database operation times out.
            DatabaseOperationError: Raised when database operation fails.
        """
        pass

    @abstractmethod
    async def exists_by_code(self, country_code: str) -> bool:
        """Check if a country exists by CountryCode.

        Raises:
            DatabaseConnectionError: Raised when cannot connect to database.
            DatabaseTimeoutError: Raised when database operation times out.
            DatabaseOperationError: Raised when database operation fails.
        """
        pass