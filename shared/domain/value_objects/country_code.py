from shared.domain.base_vo import BaseVO
from shared.domain.exceptions import InvalidCountryCodeError


class CountryCode(BaseVO[str]):
    def __init__(self, value: str):
        if not isinstance(value, str):
            raise InvalidCountryCodeError(
                f"CountryCode must be string, got {type(value).__name__}"
            )
        value = value.strip()
        if not value:
            raise InvalidCountryCodeError(f"CountryCode must be a non-empty string")
        value = value.upper()
        if len(value) != 2:
            raise InvalidCountryCodeError(f"CountryCode is invalid !")

        super().__init__(value)
