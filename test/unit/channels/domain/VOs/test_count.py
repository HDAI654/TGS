import pytest
from src.modules.channels.domain.value_objects.count import Count
from src.modules.channels.exceptions import InvalidCountError


class TestCount:
    def test_not_int_count(self):
        with pytest.raises(InvalidCountError):
            Count("ABC")
            Count(None)

    def test_count_with_float(self):
        assert isinstance(Count(1.2).value, int)

    def test_invalid_count(self):
        with pytest.raises(InvalidCountError):
            Count("abcddd")
