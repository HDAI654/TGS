import pytest
from src.modules.auth.domain.value_objects.session_id import SessionID
from src.modules.auth.exceptions import InvalidSessionIDError


class TestSessionID:
    def test_not_str_session_id(self):
        with pytest.raises(InvalidSessionIDError):
            SessionID(123)
            SessionID(None)
            SessionID(45.67)
            SessionID([])

    def test_empty_str_session_id(self):
        with pytest.raises(InvalidSessionIDError):
            SessionID("")
            SessionID(" ")
            SessionID("    ")
            SessionID("\t")

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
            with pytest.raises(InvalidSessionIDError):
                SessionID(invalid)

    def test_invalid_uuid_version(self):
        # UUID v1 (version 1)
        uuid_v1 = "uuid_v1 = '00000000-0000-1000-8000-000000000000'"

        with pytest.raises(InvalidSessionIDError):
            SessionID(uuid_v1)

    def test_valid_uuid_v4(self):
        valid = "3bb6a3ca-66dc-440e-8d11-d8cca7ad7792"
        session_id = SessionID(valid)
        assert session_id.value == valid

    def test_uuid_strip(self):
        str_id = "    3bb6a3ca-66dc-440e-8d11-d8cca7ad7792    "
        session_id = SessionID(str_id)
        assert session_id.value == str_id.strip()

    def test_uuid_case_insensitive(self):
        upper = "123E4567-E89B-12D3-A456-426614174000"
        lower = "123e4567-e89b-12d3-a456-426614174000"

        session_id1 = SessionID(upper)
        session_id2 = SessionID(lower)

        assert session_id1.value == session_id1.value.lower()
        assert session_id1.value == session_id2.value

    def test_generate_session_id(self):
        session_id = SessionID.generate()

        assert isinstance(session_id, SessionID)
        assert len(session_id.value) == 36

    def test_generate_always_unique(self):
        ids = [SessionID.generate().value for _ in range(100)]
        assert len(ids) == len(set(ids))
