"""Country query use cases.

Orchestrate read-only country retrieval. Validation covers application
contracts (pagination, search presence).
"""

from src.domain.entities.country import Country
from src.domain.ports.country_repository import CountryRepository
from src.exceptions.application import InvalidPaginationError

_MIN_LIMIT = 1
_MAX_LIMIT = 100


def _validate_pagination(limit: int, offset: int) -> None:
    if not _MIN_LIMIT <= limit <= _MAX_LIMIT:
        raise InvalidPaginationError(
            f"limit must be between {_MIN_LIMIT} and {_MAX_LIMIT}"
        )
    if offset < 0:
        raise InvalidPaginationError("offset must be non-negative")


async def get_country(
    repository: CountryRepository, country_code: str
) -> Country | None:
    """Return a single country by code, or None when not found."""
    return await repository.get_by_id(country_code)


async def search_countries(
    repository: CountryRepository,
    text: str | None,
    limit: int,
    offset: int,
) -> tuple[list[Country], int] | None:
    """Search countries by free text.

    Returns None when text is missing or blank (no search requested).
    Otherwise returns (matching items, total count) with pagination applied.
    """
    _validate_pagination(limit, offset)
    if text is None or not text.strip():
        return None
    return await repository.search(text, limit, offset)
