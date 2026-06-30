import pytest
from shared.domain.id_vo import ID
from shared.domain.exceptions import InvalidIDError


class TestID:
    def test_none_id(self):
        with pytest.raises(InvalidIDError):
            ID(None)

    def test_not_str_id(self):
        with pytest.raises(InvalidIDError):
            ID(25)

    def test_empty_str_id(self):
        with pytest.raises(InvalidIDError):
            ID("")
            ID(" ")
            ID("    ")

    def test_id_strip(self):
        str_id = "        IDDDDDDDDDDDDD           "
        id = ID(str_id)

        assert id.value == str_id.strip()

    def test_non_ASCII_id(self):
        with pytest.raises(InvalidIDError):
            ID("این یک آیدی است")

    def test_invalid_id(self):
        with pytest.raises(InvalidIDError):
            ID("A" * 15)
            ID("A" * 40)
