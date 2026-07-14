import re
from src.modules.core.base_vo import BaseVO
from src.modules.auth.exceptions import InvalidEmailError

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class Email(BaseVO[str]):
    def __init__(self, value: str):
        if not isinstance(value, str):
            raise InvalidEmailError(f"Email must be string, got {type(value).__name__}")
        value = value.strip().lower()
        if not value:
            raise InvalidEmailError("Email must be a non-empty string")
        if not EMAIL_REGEX.match(value) or len(value) > 254:
            raise InvalidEmailError("Invalid Email !")

        super().__init__(value)
