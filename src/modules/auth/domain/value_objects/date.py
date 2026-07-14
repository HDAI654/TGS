from datetime import date
from src.modules.core.base_vo import BaseVO
from src.modules.auth.exceptions import InvalidDateError


class Date(BaseVO[date]):
    def __init__(self, value: str | date):
        if not isinstance(value, date):
            if not isinstance(value, str):
                raise InvalidDateError(
                    f"Date must be string or datetime.date, got {type(value).__name__}"
                )
            value = value.strip()
            try:
                value = date.fromisoformat(value)
            except:
                raise InvalidDateError("Date got invalid value")

        super().__init__(value)
