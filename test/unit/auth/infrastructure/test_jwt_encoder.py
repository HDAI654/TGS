import pytest
from datetime import datetime, timedelta, timezone
from src.modules.core.conf import Config
import jwt
from src.modules.auth.exceptions import AuthTokenCreationError
from src.modules.auth.infrastructure.security.jwt_encoder import JWT_TokenEncoder
from src.modules.auth.domain.value_objects.user_id import UserID
from src.modules.auth.domain.value_objects.session_id import SessionID
from src.modules.auth.domain.value_objects.device import Device


class TestJWTEncoder:
    @pytest.fixture
    def encoder(self):
        return JWT_TokenEncoder()

    def test_create_access_token_payload(self, encoder):
        user_id = UserID.generate()
        session_id = SessionID.generate()
        device = Device("Android")
        token = encoder.create_access_token(user_id, session_id, device)
        payload = jwt.decode(
            token,
            Config.AUTH_TOKEN_PUBLIC_KEY,
            algorithms=[Config.AUTH_TOKEN_ALGORITHM],
        )

        assert payload["sub"] == user_id.value
        assert payload["sid"] == session_id.value
        assert payload["dev"] == device.value
        assert isinstance(payload["exp"], float)
        assert payload["type"] == "access"
        assert isinstance(payload["iat"], float)

    def test_create_refresh_token_payload(self, encoder):
        user_id = UserID.generate()
        session_id = SessionID.generate()
        device = Device("Android")
        token = encoder.create_refresh_token(user_id, session_id, device)
        payload = jwt.decode(
            token,
            Config.AUTH_TOKEN_PUBLIC_KEY,
            algorithms=[Config.AUTH_TOKEN_ALGORITHM],
        )

        assert payload["sub"] == user_id.value
        assert payload["sid"] == session_id.value
        assert payload["dev"] == device.value
        assert isinstance(payload["exp"], float)
        assert payload["type"] == "refresh"
        assert isinstance(payload["iat"], float)
