from src.core.base_vo import BaseVO


class TestBaseVO:
    def test_str_vo(self):
        vo = BaseVO("MyValue")

        assert vo.__str__() == "MyValue"

    def test_repr_vo(self):
        vo = BaseVO("MyValue")

        assert vo.__repr__() == "BaseVO('MyValue')"

    def test_eq_vo(self):
        vo = BaseVO("MyValue")
        vo2 = BaseVO("MyValue")

        assert vo == vo2

    def test_hash_vo(self):
        vo = BaseVO("MyValue")
        vo2 = BaseVO("MyValue")
        vo3 = BaseVO("MyDifferentValue")

        assert hash(vo) == hash(vo2)
        assert hash(vo) != hash(vo3) and hash(vo2) != hash(vo3)
