import jwt
from jwt import ExpiredSignatureError, InvalidTokenError, DecodeError
from src.modules.auth.domain.ports.token_decoder_interface import ITokenDecoder
from src.modules.auth.exceptions import InvalidAuthTokenError
from src.modules.core.conf import Config


class JWT_TokenDecoder(ITokenDecoder):
    def __init__(self, public_key: str = None):
        self.public_key = public_key or Config.AUTH_TOKEN_PUBLIC_KEY
        self.algorithm = Config.AUTH_TOKEN_ALGORITHM

    def decode_token(self, token: str) -> dict:
        try:
            return jwt.decode(token, self.public_key, algorithms=[self.algorithm])
        except ExpiredSignatureError:
            raise InvalidAuthTokenError("AuthToken has expired")
        except (InvalidTokenError, DecodeError):
            raise InvalidAuthTokenError(
                "AuthToken is malformed or signature is invalid"
            )

    def decode_and_validate(
        self, field_type_map: dict, token: str, expected_token_type: str = None
    ) -> dict:
        payload = self.decode_token(token)

        # Check claims
        required_claims = field_type_map.keys()
        for claim in required_claims:
            if claim not in payload:
                raise InvalidAuthTokenError(f"Missing required claim: {claim}")

        for (
            claim,
            value,
        ) in payload.items():
            if claim not in field_type_map:
                continue
            if not isinstance(value, field_type_map[claim]):
                raise InvalidAuthTokenError(f"Token is invalid or has wrong data")

        if expected_token_type and payload["type"] != expected_token_type:
            raise InvalidAuthTokenError(
                f"Invalid auth-token type: expected {expected_token_type}"
            )

        return payload
