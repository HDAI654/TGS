import jwt
from datetime import datetime, timedelta, timezone
from src.modules.auth.domain.ports.token_encoder_interface import ITokenEncoder
from src.modules.auth.domain.value_objects.user_id import UserID
from src.modules.auth.domain.value_objects.session_id import SessionID
from src.modules.auth.domain.value_objects.device import Device
from src.modules.auth.exceptions import AuthTokenCreationError
from src.modules.core.conf import Config


class JWT_TokenEncoder(ITokenEncoder):
    FIELD_TYPE_MAP = {
        "sid": str,
        "sub": str,
        "dev": str,
        "exp": float,
        "type": str,
        "iat": float,
    }

    def __init__(self, private_key: str = None):
        self.private_key = private_key or Config.AUTH_TOKEN_PRIVATE_KEY
        self.algorithm = Config.AUTH_TOKEN_ALGORITHM

    def create_access_token(
        self, user_id: UserID, session_id: SessionID, device: Device, role: str = None
    ) -> str:
        try:
            exp = datetime.now(timezone.utc) + timedelta(
                minutes=Config.ACCESS_TOKEN_EXPIRE_MINUTES
            )
            payload = {
                "sid": session_id.value,
                "sub": user_id.value,
                "dev": device.value,
                "exp": exp.timestamp(),
                "type": "access",
                "iat": datetime.now(timezone.utc).timestamp(),
            }
            if role is not None and isinstance(role, str) and len(role.strip()) > 0:
                payload["role"] = role
            return jwt.encode(payload, self.private_key, algorithm=self.algorithm)
        except Exception as e:
            raise AuthTokenCreationError(
                f"Unexpected error occurred during access-token generation:\n{str(e)}"
            )

    def create_refresh_token(
        self, user_id: UserID, session_id: SessionID, device: Device
    ) -> str:
        try:
            exp = datetime.now(timezone.utc) + timedelta(
                minutes=Config.REFRESH_TOKEN_EXPIRE_MINUTES
            )
            payload = {
                "sid": session_id.value,
                "sub": user_id.value,
                "dev": device.value,
                "exp": exp.timestamp(),
                "type": "refresh",
                "iat": datetime.now(timezone.utc).timestamp(),
            }
            return jwt.encode(payload, self.private_key, algorithm=self.algorithm)
        except Exception as e:
            raise AuthTokenCreationError(
                f"Unexpected error occurred during refresh-token generation:\n{str(e)}"
            )
