import pytest
from src.modules.auth.domain.value_objects.password import Password
from src.modules.auth.exceptions import InvalidPasswordError, WeakPasswordError


class TestPassword:
    def test_not_str_password(self):
        with pytest.raises(InvalidPasswordError):
            Password(25)
            Password(None)
            Password(3.14)
            Password([])

    def test_empty_str_password(self):
        with pytest.raises(InvalidPasswordError):
            Password("")
            Password(" ")
            Password("    ")

    def test_password_strip(self):
        str_password = "   MySecurePass123!   "
        password = Password(str_password)
        assert password.value == str_password.strip()

    def test_password_too_short(self):
        with pytest.raises(WeakPasswordError):
            Password("Abc12!@")

    def test_password_too_long(self):
        long_password = "A" * 51 + "b1!"

        with pytest.raises(WeakPasswordError):
            Password(long_password)

    def test_password_no_uppercase(self):
        with pytest.raises(WeakPasswordError):
            Password("abcdefg1!")

    def test_password_no_lowercase(self):
        with pytest.raises(WeakPasswordError):
            Password("ABCDEFG1!")

    def test_password_no_digit(self):
        with pytest.raises(WeakPasswordError):
            Password("ABCDefg!")

    def test_password_no_special(self):
        with pytest.raises(WeakPasswordError):
            Password("ABCDefg1")

    def test_valid_password(self):
        password = Password("MySecurePass123!")

        assert password.value == "MySecurePass123!"
        assert isinstance(password, Password)

    def test_valid_password_minimal(self):
        password = Password("Abc123!@")

        assert password.value == "Abc123!@"

    def test_valid_password_with_spaces(self):
        password = Password("   MySecurePass123!   ")

        assert password.value == "MySecurePass123!"

    def test_multiple_validation_errors(self):
        with pytest.raises(WeakPasswordError) as exc_info:
            Password("abc")

        errors = str(exc_info.value).split("\n")
        assert len(errors) >= 4
        assert any("at least 8" in error for error in errors)
        assert any("uppercase" in error for error in errors)
        assert any("number" in error for error in errors)
        assert any("special" in error for error in errors)

    def test_password_common_patterns(self):
        password = Password("Password1!")
        assert password.value == "Password1!"

        password = Password("12345678Aa!")
        assert password.value == "12345678Aa!"
