from src.core.base_vo import BaseVO
from src.core.exceptions import InvalidIsGeoBlockedError


class IsGeoBlocked(BaseVO[bool]):
    def __init__(self, value: bool | None = False):
        if value is None:
            value = False
        if not isinstance(value, bool):
            raise InvalidIsGeoBlockedError(
                f"IsGeoBlocked must be boolean, got {type(value).__name__}"
            )

        super().__init__(value)
