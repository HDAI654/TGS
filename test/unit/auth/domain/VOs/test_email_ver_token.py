import pytest
from src.modules.auth.domain.value_objects.email_verification_token import (
    EmailVerificationToken,
)
from src.modules.auth.exceptions import InvalidEmailVerificationTokenError


class TestEmailVerificationToken:
    def test_not_str_email_verification_token(self):
        with pytest.raises(InvalidEmailVerificationTokenError):
            EmailVerificationToken(123)
            EmailVerificationToken(None)
            EmailVerificationToken(45.67)
            EmailVerificationToken([])

    def test_empty_str_email_verification_token(self):
        with pytest.raises(InvalidEmailVerificationTokenError):
            EmailVerificationToken("")
            EmailVerificationToken(" ")
            EmailVerificationToken("    ")
            EmailVerificationToken("\t")

    def test_invalid_uuid_format(self):
        invalid_uuids = [
            "not-a-uuid",  # Not UUID format
            "123e4567-e89b-12d3-a456-42661417400",  # Too short
            "123e4567-e89b-12d3-a456-4266141740000",  # Too long
            "123e4567-e89b-12d3-a456-42661417400x",  # Invalid hex
            "123e4567-e89b-12d3-a456-42661417400!",  # Special char
            "123e4567-e89b-12d3-a456-42661417400 ",  # Trailing space
            "123e4567-e89b-12d3-a456-42661417400",  # 35 chars
        ]

        for invalid in invalid_uuids:
            with pytest.raises(InvalidEmailVerificationTokenError):
                EmailVerificationToken(invalid)

    def test_invalid_uuid_version(self):
        # UUID v1 (version 1)
        uuid_v1 = "uuid_v1 = '00000000-0000-1000-8000-000000000000'"

        with pytest.raises(InvalidEmailVerificationTokenError):
            EmailVerificationToken(uuid_v1)

    def test_valid_uuid_v4(self):
        valid = "3bb6a3ca-66dc-440e-8d11-d8cca7ad7792"
        email_verification_token = EmailVerificationToken(valid)
        assert email_verification_token.value == valid

    def test_uuid_strip(self):
        str_id = "    3bb6a3ca-66dc-440e-8d11-d8cca7ad7792    "
        email_verification_token = EmailVerificationToken(str_id)
        assert email_verification_token.value == str_id.strip()

    def test_uuid_case_insensitive(self):
        upper = "123E4567-E89B-12D3-A456-426614174000"
        lower = "123e4567-e89b-12d3-a456-426614174000"

        email_verification_token1 = EmailVerificationToken(upper)
        email_verification_token2 = EmailVerificationToken(lower)

        assert (
            email_verification_token1.value == email_verification_token1.value.lower()
        )
        assert email_verification_token1.value == email_verification_token2.value

    def test_generate_email_verification_token(self):
        email_verification_token = EmailVerificationToken.generate()

        assert isinstance(email_verification_token, EmailVerificationToken)
        assert len(email_verification_token.value) == 36

    def test_generate_always_unique(self):
        ids = [EmailVerificationToken.generate().value for _ in range(100)]
        assert len(ids) == len(set(ids))
