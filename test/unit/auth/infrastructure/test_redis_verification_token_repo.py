import pytest
import asyncio
from src.modules.auth.infrastructure.cache.redis_verification_token_repo import (
    RedisEmailVerificationTokenRepo,
)
from src.modules.auth.domain.value_objects.email import Email
from src.modules.auth.domain.value_objects.email_verification_token import (
    EmailVerificationToken,
)
from src.modules.core.conf import Config


class TestRedisEmailVerificationTokenRepo:

    @pytest.fixture
    async def token_repo(self, redis_client):
        return RedisEmailVerificationTokenRepo(redis_client)

    @pytest.fixture
    def email(self):
        return Email("test@example.com")

    @pytest.fixture
    def token(self):
        return EmailVerificationToken.generate()

    async def test_add_token(self, token_repo, redis_client, token, email):
        token_type = "verifyemail"
        key = token_repo._key_creator(token, token_type)
        ttl_seconds = Config.VERIFY_EMAIL_EXPIRE_MINUTES * 60

        await token_repo.add(token, email, token_type, ttl_seconds)

        stored_email = await redis_client.get(key)
        assert stored_email == email.value

        ttl = await redis_client.ttl(key)
        assert ttl >= ttl_seconds - 2
        assert ttl <= ttl_seconds

    async def test_get_existing_token(self, token_repo, redis_client, token, email):
        token_type = "verifyemail"
        key = token_repo._key_creator(token, token_type)
        await redis_client.setex(key, 60, email.value)

        result = await token_repo.get(token, token_type)

        assert result == email

    async def test_get_non_existent_token(self, token_repo, token):
        result = await token_repo.get(token)
        assert result is None

    async def test_delete_existing_token(self, token_repo, redis_client, token, email):
        token_type = "verifyemail"
        key = token_repo._key_creator(token, token_type)
        await redis_client.setex(key, 60, email.value)

        await token_repo.delete(token, token_type)

        exists = await redis_client.exists(key)
        assert exists == 0

    async def test_delete_non_existent_token(self, token_repo, token):
        # Should not raise any error
        await token_repo.delete(token)

    async def test_get_returns_none_for_expired_token(
        self, token_repo, redis_client, token, email
    ):
        token_type = "verifyemail"
        key = token_repo._key_creator(token, token_type)
        # Set with very short TTL and wait
        await redis_client.setex(key, 1, email.value)
        await asyncio.sleep(1.5)

        result = await token_repo.get(token, token_type)
        assert result is None

    async def test_add_with_custom_token_type(
        self, token_repo, redis_client, token, email
    ):
        token_type = "password_reset"
        key = token_repo._key_creator(token, token_type)
        await token_repo.add(token, email, token_type)

        stored_email = await redis_client.get(key)
        assert stored_email == email.value
