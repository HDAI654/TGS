import uuid
from src.modules.core.base_vo import BaseVO
from src.modules.auth.exceptions import InvalidUserIDError


class UserID(BaseVO[str]):
    """
    User ID Value Object - UUID v4 format

    Format: 3bb6a3ca-66dc-440e-8d11-d8cca7ad7792
    Length: 36 characters
    """

    UUID_VERSION = 4
    LENGTH = 36

    def __init__(self, value: str):
        if not isinstance(value, str):
            raise InvalidUserIDError(
                f"UserID must be string, got {type(value).__name__}"
            )
        value = value.strip()
        if not value:
            raise InvalidUserIDError("UserID must be a non-empty string")
        try:
            uuid_obj = uuid.UUID(value, version=self.UUID_VERSION)
            value = str(uuid_obj)
        except Exception:
            raise InvalidUserIDError(
                f"Invalid UUID v{self.UUID_VERSION} format: {value}"
            )

        super().__init__(value)

    @classmethod
    def generate(cls) -> "UserID":
        """Generate a new UserID"""
        return cls(str(uuid.uuid4()))
