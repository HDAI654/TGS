"""Seed data for in-memory repositories (development only)."""

from uuid import uuid4

from src.domain.entities.channel import Channel, Category
from src.domain.entities.country import Country
from src.infrastructure.persistence.in_memory_repos import (
    InMemoryChannelRepository,
    InMemoryCountryRepository,
)

# ---- Sample data ----
_countries = [
    Country("US", "United States", "America/New_York", True, 3),
    Country("GB", "United Kingdom", "Europe/London", True, 2),
    Country("QA", "Qatar", "Asia/Qatar", True, 1),
]

_categories = {
    1: Category(id=1, name="News"),
    2: Category(id=2, name="Sports"),
    3: Category(id=3, name="Entertainment"),
}

_channels = [
    Channel(
        id=uuid4(),
        name="CNN",
        category=_categories[1],
        language="en",
        country_code="US",
        urls=("https://cnn.com",),
    ),
    Channel(
        id=uuid4(),
        name="BBC World",
        category=_categories[1],
        language="en",
        country_code="GB",
        urls=("https://bbc.com",),
    ),
    Channel(
        id=uuid4(),
        name="Al Jazeera",
        category=_categories[1],
        language="ar",
        country_code="QA",
        urls=("https://aljazeera.com",),
    ),
    Channel(
        id=uuid4(),
        name="ESPN",
        category=_categories[2],
        language="en",
        country_code="US",
        urls=("https://espn.com",),
    ),
]

# Singleton repository instances
_country_name_map = {c.country_code: c.country_name for c in _countries}
channel_repo = InMemoryChannelRepository(_channels, country_name_map=_country_name_map)
country_repo = InMemoryCountryRepository(_countries)
