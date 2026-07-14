import pytest
from src.modules.auth.domain.value_objects.email import Email
from src.modules.auth.exceptions import InvalidEmailError


class TestEmail:
    def test_not_str_email(self):
        with pytest.raises(InvalidEmailError):
            Email(25)
            Email(None)

    def test_empty_str_email(self):
        with pytest.raises(InvalidEmailError):
            Email("")
            Email(" ")
            Email("    ")

    def test_invalid_email(self):
        with pytest.raises(InvalidEmailError):
            Email("ssss12111._com@@sjk")
            Email("A" * 65 + "@gmail.com")
            Email("Aaaaaaa@" + "g" * 256 + ".com")
            Email("A" * 235 + "@gmail.com")
            Email("A@dweuu@gmail.com")

    def test_email_strip(self):
        str_email = "        testemail@test.com  "
        email = Email(str_email)

        assert email.value == str_email.strip()

    def test_email_lower(self):
        email1 = Email("MyEmail@gmail.com")
        email2 = Email("MYEMAIL@gmail.com")

        assert email1.value == email2.value
