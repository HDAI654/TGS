from src.modules.core.base_vo import BaseVO
from src.modules.channels.exceptions import InvalidNameError


class Name(BaseVO[str]):
    def __init__(self, value: str):
        if not isinstance(value, str):
            raise InvalidNameError(f"Name must be string, got {type(value).__name__}")
        value = value.strip()
        if not value:
            raise InvalidNameError(f"Name must be a non-empty string")
        if len(value) > 100:
            raise InvalidNameError(f"Name is so long !")

        super().__init__(value)
