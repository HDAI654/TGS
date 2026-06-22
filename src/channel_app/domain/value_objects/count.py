from src.core.base_vo import BaseVO
from src.core.exceptions import InvalidCountError


class Count(BaseVO[str]):
    def __init__(self, value: int):
        value = int(value) if isinstance(value, float) else value
        if not isinstance(value, int):
            raise InvalidCountError(
                f"Count must be integer, got {type(value).__name__}"
            )
        if value < 0:
            raise InvalidCountError(f"Count can't be negative")

        super().__init__(value)
