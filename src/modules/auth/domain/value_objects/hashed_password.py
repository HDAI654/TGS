from src.modules.core.base_vo import BaseVO
from src.modules.auth.exceptions import InvalidHashedPasswordError


class HashedPassword(BaseVO[str]):
    def __init__(self, hashed_value: str):
        if not isinstance(hashed_value, str):
            raise InvalidHashedPasswordError(
                f"HashedPassword must be string, got {type(hashed_value).__name__}"
            )
        hashed_value = hashed_value.strip()
        if not hashed_value:
            raise InvalidHashedPasswordError(
                "HashedPassword must be a non-empty string"
            )

        super().__init__(hashed_value)
