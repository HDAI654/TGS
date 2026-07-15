'''import pytest
import logging
from httpx import AsyncClient, ASGITransport
from src.main import app
from src.modules.core.database import engine, Base
from src.modules.core.redis_client import get_redis_client
from src.modules.auth.infrastructure.security.jwt_decoder import JWT_TokenDecoder
from src.modules.auth.domain.ports.email_sender_interface import IEmailSender
from unittest.mock import AsyncMock
from src.modules.auth.presentation.api.v1.dependencies import (
    get_email_sender,
)


class TestAuthE2E:
    """End-to-end tests for authentication flow."""

    @pytest.fixture(scope="session")
    def event_loop(self):
        import asyncio

        loop = asyncio.new_event_loop()
        yield loop
        loop.close()

    @pytest.fixture(autouse=True)
    async def setup(self):
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        # Mock email sender
        mock_email_sender = AsyncMock(spec=IEmailSender)
        mock_email_sender.send.return_value = None

        logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
        logging.getLogger("aiosqlite").setLevel(logging.WARNING)

        # Override dependencies
        app.dependency_overrides[get_email_sender] = lambda: mock_email_sender

        yield

        app.dependency_overrides.clear()
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

        redis = get_redis_client()
        keys = await redis.keys(f"rl_*")
        for key in keys:
            await redis.delete(key)

    @pytest.fixture
    async def client(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(
            transport=transport, base_url="http://test/api/v1"
        ) as client:
            yield client

    @pytest.fixture
    def user_data(self):
        return {"email": "e2e_test@example.com", "password": "StrongP@ssw0rd123!"}

    async def _get_verification_token_from_redis(self, redis, email: str) -> str:
        keys = await redis.keys("verifyemail:*")
        for key in keys:
            value = await redis.get(key)
            if value and value == email:
                return key.split(":")[1]
        return None

    async def _get_reset_token_from_redis(self, redis, email: str) -> str:
        keys = await redis.keys("forget_pass_verify:*")
        for key in keys:
            value = await redis.get(key)
            if value and value == email:
                return key.split(":")[1]
        return None

    async def test_complete_auth_flow(self, client, user_data):
        email = user_data["email"]
        password = user_data["password"]
        new_password = "NewStrongP@ssw0rd456!"

        # 1. Send verification email
        response = await client.post("/auth/verify-email/send", json={"email": email})
        assert response.status_code == 200

        redis = get_redis_client()
        token = await self._get_verification_token_from_redis(redis, email)
        assert token is not None

        # 2. Signup
        response = await client.post(
            "/auth/signup",
            json={"verify_token": token, "password": password},
        )
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert "device_id" in data
        access_token = data["access_token"]
        refresh_token = data["refresh_token"]

        # 3. Login
        response = await client.post(
            "/auth/login",
            json={"email": email, "password": password},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert "device_id" in data
        device = data["device_id"]

        # 4. Change password
        response = await client.put(
            "/auth/password",
            json={"access_token": data["access_token"], "new_password": new_password},
            headers={"X-Device-Id": device},
        )
        assert response.status_code == 200
        assert response.json()["message"] == "Password changed successfully"

        # 4.5. Forget password - request reset
        response = await client.post(
            "/auth/forget-password",
            json={"email": email},
        )
        assert response.status_code == 200
        assert response.json()["message"] == "Reset password email sent successfully"

        # Get reset password token from Redis
        reset_token = await self._get_reset_token_from_redis(redis, email)
        assert reset_token is not None

        # 4.6. Reset password with token
        new_reset_password = "ResetP@ssw0rd789!"
        response = await client.post(
            "/auth/reset-password",
            json={"verify_token": reset_token, "new_password": new_reset_password},
        )
        assert response.status_code == 200
        assert response.json()["message"] == "Password reset successfully."

        # 4.7. Login with reset password
        response = await client.post(
            "/auth/login",
            json={"email": email, "password": new_reset_password},
        )
        assert response.status_code == 200
        data = response.json()
        access_token = data["access_token"]
        device = data["device_id"]

        # 5. Login with new password (using reset password)
        response = await client.post(
            "/auth/login",
            json={"email": email, "password": new_reset_password},
        )
        assert response.status_code == 200
        access_token = response.json()["access_token"]
        device = response.json()["device_id"]

        # 6. Logout
        response = await client.post(
            "/auth/logout",
            json={"access_token": access_token},
            headers={"X-Device-Id": device},
        )
        assert response.status_code == 200
        assert response.json()["message"] == "Logged out successfully"

        # 7. Login again
        response = await client.post(
            "/auth/login",
            json={"email": email, "password": new_reset_password},
        )
        assert response.status_code == 200
        access_token = response.json()["access_token"]
        refresh_token = response.json()["refresh_token"]
        device = response.json()["device_id"]

        # 8. Refresh token
        response = await client.post(
            "/auth/token/refresh",
            json={"refresh_token": refresh_token},
            headers={"X-Device-Id": device},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data

        # 9. Revoke a session
        decoder = JWT_TokenDecoder()
        payload = decoder.decode_token(access_token)
        session_id = payload["sid"]

        response = await client.delete(
            f"/auth/sessions/{session_id}",
            headers={"Authorization": f"Bearer {access_token}", "X-Device-Id": device},
        )
        assert response.status_code == 200
        assert (
            f"Session {session_id} revoked successfully" in response.json()["message"]
        )

        # 10. Revoke all other sessions
        response = await client.post(
            "/auth/login",
            json={"email": email, "password": new_reset_password},
        )
        assert response.status_code == 200
        access_token = response.json()["access_token"]
        device = response.json()["device_id"]

        response = await client.delete(
            "/auth/sessions",
            headers={"Authorization": f"Bearer {access_token}", "X-Device-Id": device},
        )
        assert response.status_code == 200
        assert response.json()["message"] == "All other sessions revoked successfully"

        # 11. Delete account
        response = await client.post(
            "/auth/login",
            json={"email": email, "password": new_reset_password},
        )
        assert response.status_code == 200
        access_token = response.json()["access_token"]
        device = response.json()["device_id"]

        response = await client.delete(
            "/auth/account",
            headers={"Authorization": f"Bearer {access_token}", "X-Device-Id": device},
        )
        assert response.status_code == 200
        assert response.json()["message"] == "Account deleted successfully"

        # Verify login fails
        response = await client.post(
            "/auth/login",
            json={"email": email, "password": new_reset_password},
        )
        assert response.status_code == 401
'''
