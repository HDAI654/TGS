from src.modules.core.base_vo import BaseVO


class BaseBoolVO(BaseVO[bool]):
    def __init__(self, exception, value: bool):
        if not isinstance(value, bool):
            raise exception(
                f"{self.__class__.__name__} must be boolean, got {type(value).__name__}"
            )

        super().__init__(value)
