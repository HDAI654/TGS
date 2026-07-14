import pytest
from src.modules.auth.infrastructure.security.block_email_checker import (
    ImpEmailChecker,
    BLOCKLIST,
)
from src.modules.auth.domain.value_objects.email import Email


@pytest.fixture
async def checker():
    return ImpEmailChecker()


async def test_with_non_blocked_email(checker):
    assert await checker.is_blocked(email=Email("example@gmail.com")) is False


async def test_with_blocked_email(checker):
    assert (
        await checker.is_blocked(email=Email(f"example@{list(BLOCKLIST)[0]}")) is True
    )
