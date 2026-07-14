import pytest
from src.modules.auth.infrastructure.security.bcrypt_password_hasher import (
    BcryptPasswordHasher,
)
from src.modules.auth.domain.value_objects.password import Password
from src.modules.auth.domain.value_objects.hashed_password import HashedPassword


class TestBcryptPasswordHasher:

    @pytest.fixture
    def hasher(self):
        return BcryptPasswordHasher()

    def test_hash_returns_hashed_password_vo(self, hasher):
        password = Password("StrongPassword123!")
        hashed = hasher.hash(password)

        assert isinstance(hashed, HashedPassword)
        assert hashed.value != password.value

    def test_hash_same_password_generates_different_hashes(self, hasher):
        password = Password("StrongPassword123!")
        hash1 = hasher.hash(password)
        hash2 = hasher.hash(password)

        assert hash1.value != hash2.value

    def test_verify_correct_password_returns_true(self, hasher):
        password = Password("Strong@@Password123!")
        hashed = hasher.hash(password)

        assert hasher.verify(password, hashed) is True

    def test_verify_wrong_password_returns_false(self, hasher):
        password = Password("Strong@@Password123!")
        hashed = hasher.hash(password)
        wrong_password = Password("WrongPassword855!")

        assert hasher.verify(wrong_password, hashed) is False

    def test_hash_with_unicode_characters(self, hasher):
        password = Password("密码1LLekk23!@#")
        hashed = hasher.hash(password)

        assert hasher.verify(password, hashed) is True
