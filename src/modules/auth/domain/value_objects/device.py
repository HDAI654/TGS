from src.modules.core.base_vo import BaseVO
from src.modules.auth.exceptions import InvalidDeviceError


class Device(BaseVO[str]):
    def __init__(self, value: str):
        if not isinstance(value, str):
            raise InvalidDeviceError(
                f"Device must be string, got {type(value).__name__}"
            )
        value = value.strip()
        if not value:
            raise InvalidDeviceError("Device must be a non-empty string")

        if len(value) > 50:
            raise InvalidDeviceError("Invalid Device")

        super().__init__(value)
