import pytest
from unittest.mock import call
from src.modules.auth.exceptions import (
    DeviceMismatchError,
    PermissionDenied,
    SessionNotFoundError,
)
from src.modules.auth.domain.value_objects.session_id import SessionID
from src.modules.auth.domain.value_objects.user_id import UserID
from src.modules.auth.domain.entities.session import SessionEntity
from src.modules.auth.domain.value_objects.device import Device


async def test_revoke_success(revoke_service, mock_session_repo, mock_session_entity):
    mock_session_repo.get_by_id.return_value = mock_session_entity
    access_token = "valid-token"
    session_id = "38cffd95-3126-435c-b46b-6a67b8e57607"
    current_device = "chrome-windows"

    await revoke_service.execute(access_token, session_id, current_device)

    mock_session_repo.get_by_id.assert_has_calls(
        [
            call(SessionID("38cffd95-3126-435c-b46b-6a67b8e57607")),
            call(SessionID(session_id)),
        ]
    )
    mock_session_repo.delete.assert_called_once_with(
        session_id=SessionID(session_id),
        user_id=UserID("8e89fa33-3f7c-4a98-bcf6-fec97b92dd43"),
    )


async def test_revoke_device_mismatch(revoke_service):
    access_token = "valid-token"
    session_id = "some-session"
    current_device = "firefox-linux"

    with pytest.raises(DeviceMismatchError):
        await revoke_service.execute(access_token, session_id, current_device)


async def test_revoke_permission_denied(revoke_service, mock_session_repo):
    # Session belongs to a different user
    different_user_session = SessionEntity.create(
        id="38cffd95-3126-435c-b46b-6a67b8e57607",
        user_id=UserID.generate().value,
        device=Device("chrome-windows").value,
    )
    mock_session_repo.get_by_id.return_value = different_user_session

    access_token = "valid-token"
    session_id = "38cffd95-3126-435c-b46b-6a67b8e57607"
    current_device = "chrome-windows"

    with pytest.raises(PermissionDenied):
        await revoke_service.execute(access_token, session_id, current_device)


async def test_revoke_user_current_session_not_found(revoke_service, mock_session_repo):
    access_token = "valid-token"
    current_device = "chrome-windows"

    mock_session_repo.get_by_id.side_effect = SessionNotFoundError

    with pytest.raises(SessionNotFoundError):
        await revoke_service.execute(access_token, SessionID.generate(), current_device)
