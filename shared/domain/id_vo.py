from shared.domain.base_vo import BaseVO
from shared.domain.exceptions import InvalidIDError


class ID(BaseVO[str]):
    STANDARD_ID_LENGTH = 14

    def __init__(self, value: str):
        if not isinstance(value, str):
            raise InvalidIDError(f"ID must be string, got {type(value).__name__}")
        value = value.strip()
        if not value:
            raise InvalidIDError("ID must be a non-empty string")
        if not value.isascii():
            raise InvalidIDError("ID must contain only ASCII characters")
        if len(value) != 14:
            raise InvalidIDError("Invalid ID !")

        super().__init__(value)
