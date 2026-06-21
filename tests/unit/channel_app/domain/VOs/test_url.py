import pytest
from src.channel_app.domain.value_objects.url import URL
from src.core.exceptions import InvalidURLError


class TestURL:
    def test_not_str_URL(self):
        with pytest.raises(InvalidURLError):
            URL(25)
            URL(None)

    def test_empty_str_URL(self):
        with pytest.raises(InvalidURLError):
            URL("")
            URL(" ")
            URL("  ")

    def test_URL_strip(self):
        str_URL = "        http://swwdw.wdwd  "
        url = URL(str_URL)

        assert url.value == str_URL.strip()

    def test_long_URL(self):
        with pytest.raises(InvalidURLError):
            URL("MyURL" + "ABC" * 2050)
    
    def test_URL_with_not_allowed_scheme(self):
        with pytest.raises(InvalidURLError):
            URL("hjej://ejcnec.edji")
    
    def test_URL_without_hostname(self):
        with pytest.raises(InvalidURLError):
            URL("http://")
    
    def test_with_invalid_format(self):
        with pytest.raises(InvalidURLError):
            URL("hello:)")
