from src.modules.core.base_vo import BaseVO
from src.modules.channels.domain.exceptions import InvalidCategoryNameError


class CategoryName(BaseVO[str]):
    def __init__(self, value: str):
        if not isinstance(value, str):
            raise InvalidCategoryNameError(
                f"CategoryName must be string, got {type(value).__name__}"
            )
        value = value.strip()
        if not value:
            raise InvalidCategoryNameError(f"CategoryName must be a non-empty string")
        if len(value) > 100:
            raise InvalidCategoryNameError(f"CategoryName is so long !")
        value = value.lower().title()

        super().__init__(value)
