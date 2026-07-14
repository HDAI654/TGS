from src.modules.core.base_vo import BaseVO
from src.modules.channels.exceptions import InvalidCategoryError


class Category(BaseVO[str]):
    def __init__(self, value: str):
        if not isinstance(value, str):
            raise InvalidCategoryError(
                f"Category must be string, got {type(value).__name__}"
            )
        value = value.strip()
        if not value:
            raise InvalidCategoryError(f"Category must be a non-empty string")
        if len(value) > 100:
            raise InvalidCategoryError(f"Category is so long !")
        value = value.lower().title()

        super().__init__(value)
