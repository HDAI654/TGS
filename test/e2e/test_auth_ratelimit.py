'''import pytest
import fakeredis
from unittest.mock import patch
from httpx import AsyncClient, ASGITransport
from src.main import app
from src.modules.core.database import engine, Base
from src.modules.core.redis_client import get_redis_client
from src.modules.auth.presentation.api.v1.del_account import (
    RATE_LIMIT_MAX_REQUESTS as DEL_ACC_RATE_LIMIT_MAX_REQUESTS,
)
from src.modules.auth.presentation.api.v1.forget_pass_verify import (
    RATE_LIMIT_MAX_REQUESTS as FORGET_PASS_RATE_LIMIT_MAX_REQUESTS,
)
from src.modules.auth.presentation.api.v1.login import (
    RATE_LIMIT_MAX_REQUESTS as LOGIN_RATE_LIMIT_MAX_REQUESTS,
)
from src.modules.auth.presentation.api.v1.logout import (
    RATE_LIMIT_MAX_REQUESTS as LOGOUT_RATE_LIMIT_MAX_REQUESTS,
)
from src.modules.auth.presentation.api.v1.reset_password import (
    RATE_LIMIT_MAX_REQUESTS as RESET_PASS_RATE_LIMIT_MAX_REQUESTS,
)
from src.modules.auth.presentation.api.v1.revoke_all_other import (
    RATE_LIMIT_MAX_REQUESTS as REVOKE_ALL_RATE_LIMIT_MAX_REQUESTS,
)
from src.modules.auth.presentation.api.v1.revoke import (
    RATE_LIMIT_MAX_REQUESTS as REVOKE_RATE_LIMIT_MAX_REQUESTS,
)
from src.modules.auth.presentation.api.v1.send_verification import (
    RATE_LIMIT_MAX_REQUESTS as SEND_VERIFY_RATE_LIMIT_MAX_REQUESTS,
)
from src.modules.auth.presentation.api.v1.set_password import (
    RATE_LIMIT_MAX_REQUESTS as SET_PASS_RATE_LIMIT_MAX_REQUESTS,
)
from src.modules.auth.presentation.api.v1.signup import (
    RATE_LIMIT_MAX_REQUESTS as SIGNUP_RATE_LIMIT_MAX_REQUESTS,
)
from src.modules.auth.presentation.api.v1.token_rotation import (
    RATE_LIMIT_MAX_REQUESTS as ROTATION_RATE_LIMIT_MAX_REQUESTS,
)

import asyncio
from src.modules.core.conf import Config

_redis_clients = {}


async def patched_get_redis():
    loop = asyncio.get_running_loop()
    if loop not in _redis_clients:
        import fakeredis

        _redis_clients[loop] = fakeredis.aioredis.FakeRedis(decode_responses=True)
    return _redis_clients[loop]


class TestAuthRateLimit:
    @pytest.fixture(autouse=True)
    async def setup_db(self):
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        yield

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    @pytest.fixture(autouse=True)
    async def setup_redis(self):
        """Create fresh Redis for each test"""
        redis = fakeredis.aioredis.FakeRedis(decode_responses=True)

        # Override for both direct calls and FastAPI dependency injection
        with patch(
            "src.modules.core.redis_client.get_redis_client", return_value=redis
        ):
            app.dependency_overrides[get_redis_client] = lambda: redis
            yield
            app.dependency_overrides.clear()

        await redis.aclose()

    @pytest.fixture(autouse=True)
    def patch_rate_limiter_redis(self):
        with patch(
            "src.modules.auth.presentation.api.v1.rate_limiter.get_redis",
            new=patched_get_redis,
        ):
            yield

    @pytest.fixture
    async def client(self):
        """HTTP client for testing"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            yield client

    @pytest.fixture
    def user_data(self):
        return {
            "email": "e2e_test@example.com",
            "password": "StrongP@ssw0rd123",
        }

    # ========== Rate Limiting ==========
    async def test_rate_limiting_on_del_acc(self, client):
        for _ in range(DEL_ACC_RATE_LIMIT_MAX_REQUESTS):
            response = await client.delete(
                "/api/v1/auth/account",
                headers={"Authorization": "Bearer fake_token_for_rate_limit_test"},
            )
            assert response.status_code != 429

        # Next request should be rate limited
        response = await client.delete(
            "/api/v1/auth/account",
            headers={"Authorization": "Bearer fake_token_for_rate_limit_test"},
        )
        assert response.status_code == 429
        assert "Rate limit exceeded" in response.json()["detail"]

    async def test_rate_limiting_on_forget_pass(self, client):
        for _ in range(FORGET_PASS_RATE_LIMIT_MAX_REQUESTS):
            response = await client.post(
                "/api/v1/auth/forget-password",
                json={"email": "example.email@example.com"},
            )
            assert response.status_code != 429

        # Next request should be rate limited
        response = await client.post(
            "/api/v1/auth/forget-password",
            json={"email": "example.email@example.com"},
        )
        assert response.status_code == 429
        assert "Rate limit exceeded" in response.json()["detail"]

    async def test_rate_limiting_on_login(self, client, user_data):
        for i in range(LOGIN_RATE_LIMIT_MAX_REQUESTS):
            response = await client.post(
                "/api/v1/auth/login",
                json={
                    "email": f"register_test_{i}@example.com",
                    "password": user_data["password"],
                },
            )
            assert response.status_code != 429

        # Next request should be rate limited
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": f"register_test_f@example.com",
                "password": user_data["password"],
            },
        )
        assert response.status_code == 429
        assert "Rate limit exceeded" in response.json()["detail"]

    async def test_rate_limiting_on_logout(self, client):
        for _ in range(LOGOUT_RATE_LIMIT_MAX_REQUESTS):
            response = await client.post(
                "/api/v1/auth/logout",
                json={
                    "access_token": "fake_token_for_rate_limit_test",
                },
            )
            assert response.status_code != 429

        # Next request should be rate limited
        response = await client.post(
            "/api/v1/auth/logout",
            json={
                "access_token": "fake_token_for_rate_limit_test",
            },
        )
        assert response.status_code == 429
        assert "Rate limit exceeded" in response.json()["detail"]

    async def test_rate_limiting_on_reset_pass(self, client):
        for _ in range(RESET_PASS_RATE_LIMIT_MAX_REQUESTS):
            response = await client.post(
                "/api/v1/auth/reset-password",
                json={
                    "verify_token": "fake_token_for_rate_limit_test",
                    "new_password": "Strong@##pasww55",
                },
            )
            assert response.status_code != 429

        # Next request should be rate limited
        response = await client.post(
            "/api/v1/auth/reset-password",
            json={
                "verify_token": "fake_token_for_rate_limit_test",
                "new_password": "Strong@##pasww55",
            },
        )
        assert response.status_code == 429
        assert "Rate limit exceeded" in response.json()["detail"]

    async def test_rate_limiting_on_revoke_all(self, client):
        for _ in range(REVOKE_ALL_RATE_LIMIT_MAX_REQUESTS):
            response = await client.delete(
                "/api/v1/auth/sessions",
                headers={"Authorization": "Bearer fake_token_for_rate_limit_test"},
            )
            assert response.status_code != 429

        # Next request should be rate limited
        response = await client.delete(
            "/api/v1/auth/sessions",
            headers={"Authorization": "Bearer fake_token_for_rate_limit_test"},
        )
        assert response.status_code == 429
        assert "Rate limit exceeded" in response.json()["detail"]

    async def test_rate_limiting_on_revoke(self, client):
        for _ in range(REVOKE_RATE_LIMIT_MAX_REQUESTS):
            response = await client.delete(
                "/api/v1/auth/sessions/e5ewde5",
                headers={"Authorization": "Bearer fake_token_for_rate_limit_test"},
            )
            assert response.status_code != 429

        # Next request should be rate limited
        response = await client.delete(
            "/api/v1/auth/sessions/e5ewde5",
            headers={"Authorization": "Bearer fake_token_for_rate_limit_test"},
        )
        assert response.status_code == 429
        assert "Rate limit exceeded" in response.json()["detail"]

    async def test_rate_limiting_on_send_verify(self, client):
        for _ in range(SEND_VERIFY_RATE_LIMIT_MAX_REQUESTS):
            response = await client.post(
                "/api/v1/auth/verify-email/send",
                json={"email": "example-email@example.com"},
            )
            assert response.status_code != 429

        # Next request should be rate limited
        response = await client.post(
            "/api/v1/auth/verify-email/send",
            json={"email": "example-email@example.com"},
        )
        assert response.status_code == 429
        assert "Rate limit exceeded" in response.json()["detail"]

    async def test_rate_limiting_on_set_pass(self, client):
        for _ in range(SET_PASS_RATE_LIMIT_MAX_REQUESTS):
            response = await client.put(
                "/api/v1/auth/password",
                json={
                    "new_password": "Strong@##pasww55",
                    "access_token": "fake_token_for_rate_limit_test",
                },
            )
            assert response.status_code != 429

        # Next request should be rate limited
        response = await client.put(
            "/api/v1/auth/password",
            json={
                "new_password": "Strong@##pasww55",
                "access_token": "fake_token_for_rate_limit_test",
            },
        )
        assert response.status_code == 429
        assert "Rate limit exceeded" in response.json()["detail"]

    async def test_rate_limiting_on_signup(self, client):
        for _ in range(SIGNUP_RATE_LIMIT_MAX_REQUESTS):
            response = await client.post(
                "/api/v1/auth/signup",
                json={
                    "verify_token": "fake_token_for_rate_limit_test",
                    "password": "Strong@##pasww55",
                },
            )
            assert response.status_code != 429

        # Next request should be rate limited
        response = await client.post(
            "/api/v1/auth/signup",
            json={
                "verify_token": "fake_token_for_rate_limit_test",
                "password": "Strong@##pasww55",
            },
        )
        assert response.status_code == 429
        assert "Rate limit exceeded" in response.json()["detail"]

    async def test_rate_limiting_on_rotation(self, client):
        for _ in range(ROTATION_RATE_LIMIT_MAX_REQUESTS):
            response = await client.post(
                "/api/v1/auth/token/refresh",
                json={
                    "refresh_token": "fake_token_for_rate_limit_test",
                },
            )
            assert response.status_code != 429

        # Next request should be rate limited
        response = await client.post(
            "/api/v1/auth/token/refresh",
            json={
                "refresh_token": "fake_token_for_rate_limit_test",
            },
        )
        assert response.status_code == 429
        assert "Rate limit exceeded" in response.json()["detail"]
'''
