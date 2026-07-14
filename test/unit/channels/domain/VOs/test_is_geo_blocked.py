import pytest
from src.modules.channels.domain.value_objects.is_geo_blocked import IsGeoBlocked
from src.modules.channels.exceptions import InvalidIsGeoBlockedError


class TestIsGeoBlocked:
    def test_is_geo_blocked_with_none(self):
        vo = IsGeoBlocked(None)
        assert vo.value is False

    def test_not_bool_is_geo_blocked(self):
        with pytest.raises(InvalidIsGeoBlockedError):
            IsGeoBlocked(25)
            IsGeoBlocked("ABC")
