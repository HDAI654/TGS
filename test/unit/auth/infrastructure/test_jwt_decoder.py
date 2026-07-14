import pytest
from datetime import datetime, timedelta, timezone
from src.modules.core.conf import Config
import jwt
from src.modules.auth.exceptions import InvalidAuthTokenError
from src.modules.auth.infrastructure.security.jwt_decoder import JWT_TokenDecoder
from src.modules.auth.infrastructure.security.jwt_encoder import JWT_TokenEncoder
from src.modules.auth.domain.value_objects.user_id import UserID
from src.modules.auth.domain.value_objects.session_id import SessionID
from src.modules.auth.domain.value_objects.device import Device


class TestJWTDecoder:
    @pytest.fixture
    def decoder(self):
        return JWT_TokenDecoder()

    @pytest.fixture
    def encoder(self):
        return JWT_TokenEncoder()

    def test_decode_token_returns_payload(self, decoder):
        user_id = UserID.generate()
        session_id = SessionID.generate()
        device = Device("Adnroid")
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
        token = jwt.encode(
            payload,
            Config.AUTH_TOKEN_PRIVATE_KEY,
            algorithm=Config.AUTH_TOKEN_ALGORITHM,
        )
        decoded_payload = decoder.decode_token(token)

        assert payload == decoded_payload

    def test_decode_token_invalid_token(self, decoder):
        with pytest.raises(InvalidAuthTokenError):
            decoder.decode_token("this.is.not.a.valid.jwt")

    def test_decode_token_expired_token(self, decoder):
        user_id = UserID.generate()
        session_id = SessionID.generate()
        device = Device("Adnroid")
        exp = datetime.now(timezone.utc) - timedelta(
            days=1,
        )
        payload = {
            "sid": session_id.value,
            "sub": user_id.value,
            "dev": device.value,
            "exp": exp.timestamp(),
            "type": "access",
            "iat": datetime.now(timezone.utc).timestamp(),
        }
        token = jwt.encode(
            payload,
            Config.AUTH_TOKEN_PRIVATE_KEY,
            algorithm=Config.AUTH_TOKEN_ALGORITHM,
        )

        with pytest.raises(InvalidAuthTokenError):
            decoder.decode_token(token)

    def test_decode_token_invalid_signature(self, decoder):
        user_id = UserID.generate()
        session_id = SessionID.generate()
        device = Device("Adnroid")
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
        valid_token = jwt.encode(
            payload,
            Config.AUTH_TOKEN_PRIVATE_KEY,
            algorithm=Config.AUTH_TOKEN_ALGORITHM,
        )

        parts = valid_token.split(".")
        tampered_token = f"{parts[0]}.{parts[1]}.tampered_signature"

        with pytest.raises(InvalidAuthTokenError):
            decoder.decode_token(tampered_token)

    def test_decode_and_validate_success(self, decoder, encoder):
        user_id = UserID.generate()
        session_id = SessionID.generate()
        device = Device("Adnroid")
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
        token = jwt.encode(
            payload,
            Config.AUTH_TOKEN_PRIVATE_KEY,
            algorithm=Config.AUTH_TOKEN_ALGORITHM,
        )

        decoder.decode_and_validate(encoder.FIELD_TYPE_MAP, token)

    def test_decode_and_validate_missing_required_claim(self, decoder, encoder):
        user_id = UserID.generate()
        session_id = SessionID.generate()
        device = Device("Adnroid")
        exp = datetime.now(timezone.utc) + timedelta(
            minutes=Config.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        payload = {
            "sid": session_id.value,
            # No user_id
            "dev": device.value,
            "exp": exp.timestamp(),
            "type": "access",
            "iat": datetime.now(timezone.utc).timestamp(),
        }
        token = jwt.encode(
            payload,
            Config.AUTH_TOKEN_PRIVATE_KEY,
            algorithm=Config.AUTH_TOKEN_ALGORITHM,
        )

        with pytest.raises(InvalidAuthTokenError):
            decoder.decode_and_validate(encoder.FIELD_TYPE_MAP, token)

    def test_decode_and_validate_exp_wrong_type(self, decoder, encoder):
        user_id = UserID.generate()
        session_id = SessionID.generate()
        device = Device("Adnroid")
        payload = {
            "sid": session_id.value,
            "sub": user_id.value,
            "dev": device.value,
            "exp": "not_a_number",
            "type": "access",
            "iat": datetime.now(timezone.utc).timestamp(),
        }
        token = jwt.encode(
            payload,
            Config.AUTH_TOKEN_PRIVATE_KEY,
            algorithm=Config.AUTH_TOKEN_ALGORITHM,
        )

        with pytest.raises(InvalidAuthTokenError):
            decoder.decode_and_validate(encoder.FIELD_TYPE_MAP, token)

    def test_decode_and_validate_type_wrong_type(self, decoder, encoder):
        user_id = UserID.generate()
        session_id = SessionID.generate()
        device = Device("Adnroid")
        exp = datetime.now(timezone.utc) + timedelta(
            minutes=Config.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        payload = {
            "sid": session_id.value,
            "sub": user_id.value,
            "dev": device.value,
            "exp": exp.timestamp(),
            "type": 15528,
            "iat": datetime.now(timezone.utc).timestamp(),
        }
        token = jwt.encode(
            payload,
            Config.AUTH_TOKEN_PRIVATE_KEY,
            algorithm=Config.AUTH_TOKEN_ALGORITHM,
        )

        with pytest.raises(InvalidAuthTokenError):
            decoder.decode_and_validate(encoder.FIELD_TYPE_MAP, token)

    def test_decode_and_validate_with_expected_type_matches(self, decoder, encoder):
        user_id = UserID.generate()
        session_id = SessionID.generate()
        device = Device("Adnroid")
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
        token = jwt.encode(
            payload,
            Config.AUTH_TOKEN_PRIVATE_KEY,
            algorithm=Config.AUTH_TOKEN_ALGORITHM,
        )

        result = decoder.decode_and_validate(
            encoder.FIELD_TYPE_MAP, token, expected_token_type="access"
        )

        assert result["type"] == "access"

    def test_decode_and_validate_with_expected_type_mismatch(self, decoder, encoder):
        user_id = UserID.generate()
        session_id = SessionID.generate()
        device = Device("Adnroid")
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
        token = jwt.encode(
            payload,
            Config.AUTH_TOKEN_PRIVATE_KEY,
            algorithm=Config.AUTH_TOKEN_ALGORITHM,
        )

        with pytest.raises(InvalidAuthTokenError):
            decoder.decode_and_validate(
                encoder.FIELD_TYPE_MAP, token, expected_token_type="refresh"
            )
