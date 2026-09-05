from src.modules.core.base_vo import BaseVO
from src.modules.channels.domain.exceptions import InvalidTimezoneError


class Timezone(BaseVO[str]):
    def __init__(self, value: str):
        if not isinstance(value, str):
            raise InvalidTimezoneError(
                f"Timezone must be string, got {type(value).__name__}"
            )
        value = value.strip()
        if not value:
            raise InvalidTimezoneError(f"Timezone must be a non-empty string")
        if len(value) > 50:
            raise InvalidTimezoneError(f"Timezone is so long !")

        super().__init__(value)
