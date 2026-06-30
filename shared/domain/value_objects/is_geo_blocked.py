from shared.domain.exceptions import InvalidIsGeoBlockedError
from shared.domain.value_objects.base_bool_vo import BaseBoolVO


class IsGeoBlocked(BaseBoolVO):
    def __init__(self, value: bool | None = False):
        if value is None:
            value = False

        super().__init__(InvalidIsGeoBlockedError, value)
