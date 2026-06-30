from shared.domain.base_vo import BaseVO
from shared.domain.exceptions import InvalidTimezoneError
from src.core.conf import Config


class Timezone(BaseVO[str]):
    def __init__(self, value: str):
        if not isinstance(value, str):
            raise InvalidTimezoneError(
                f"Timezone must be string, got {type(value).__name__}"
            )
        value = value.strip()
        if not value:
            raise InvalidTimezoneError(f"Timezone must be a non-empty string")
        if value not in Config.ALLOWED_TIMEZONE:
            raise InvalidTimezoneError(f"Invalid Timezone !")

        super().__init__(value)
