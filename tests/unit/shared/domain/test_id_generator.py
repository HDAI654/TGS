from shared.domain.crypto_utils import IDGenerator


class TestIDGenerator:
    def test_creating_id_successfully(self):
        for _ in range(50):
            id = IDGenerator.generate()
            assert isinstance(id, str) and len(id) == 14
