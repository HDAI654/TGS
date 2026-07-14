from abc import ABC, abstractmethod


class ITokenDecoder(ABC):
    @abstractmethod
    def decode_token(self, token: str) -> dict:
        """
        Decode and verify a token.

        Raises:
            InvalidAuthTokenError: If the token is invalid, malformed, or expired.
        """
        pass

    @abstractmethod
    def decode_and_validate(
        self, field_type_map: dict, token: str, expected_token_type: str = None
    ) -> dict:
        """
        Decode a token and validate its claims.

        Raises:
            InvalidAuthTokenError: If the token is invalid, malformed, expired, missing required claims, or has an incorrect type.
        """

        pass
