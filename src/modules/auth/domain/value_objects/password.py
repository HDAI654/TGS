import re
from src.modules.core.base_vo import BaseVO
from src.modules.auth.exceptions import InvalidPasswordError, WeakPasswordError


class Password(BaseVO[str]):
    MIN_LENGTH = 8
    MAX_LENGTH = 50

    UPPERCASE = re.compile(r"[A-Z]")
    LOWERCASE = re.compile(r"[a-z]")
    DIGIT = re.compile(r"[0-9]")
    SPECIAL = re.compile(r'[!@#$%^&*(),.?":{}|<>]')

    def __init__(self, value: str):
        if not isinstance(value, str):
            raise InvalidPasswordError(
                f"Password must be string, got {type(value).__name__}"
            )

        value = value.strip()
        if not value:
            raise InvalidPasswordError("Password must be a non-empty string")

        self._validate_strength(value)

        super().__init__(value)

    def _validate_strength(self, password: str) -> None:
        """Validate password strength"""
        errors = self._get_validation_errors(password)
        if errors:
            raise WeakPasswordError("\n".join(errors))

    def _get_validation_errors(self, password: str) -> list[str]:
        """Get list of validation errors"""
        errors = []

        # Length checks
        if len(password) < self.MIN_LENGTH:
            errors.append(f"Password must be at least {self.MIN_LENGTH} characters")

        if len(password) > self.MAX_LENGTH:
            errors.append(f"Password must be less than {self.MAX_LENGTH} characters")

        # Character checks
        if not self.UPPERCASE.search(password):
            errors.append("Password must contain at least one uppercase letter")

        if not self.LOWERCASE.search(password):
            errors.append("Password must contain at least one lowercase letter")

        if not self.DIGIT.search(password):
            errors.append("Password must contain at least one number")

        if not self.SPECIAL.search(password):
            errors.append("Password must contain at least one special character")

        return errors
