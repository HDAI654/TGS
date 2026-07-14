import pytest
from src.modules.auth.exceptions import DeviceMismatchError, SessionNotFoundError
from src.modules.auth.domain.value_objects.session_id import SessionID
from src.modules.auth.domain.value_objects.user_id import UserID


async def test_revoke_all_other_success(revoke_all_other_service, mock_session_repo):
    access_token = "valid-token"
    current_device = "chrome-windows"

    await revoke_all_other_service.execute(access_token, current_device)

    mock_session_repo.delete_all_other_sessions.assert_called_once_with(
        current_session_id=SessionID("38cffd95-3126-435c-b46b-6a67b8e57607"),
        user_id=UserID("8e89fa33-3f7c-4a98-bcf6-fec97b92dd43"),
    )


async def test_revoke_all_other_device_mismatch(revoke_all_other_service):
    access_token = "valid-token"
    current_device = "firefox-linux"

    with pytest.raises(DeviceMismatchError):
        await revoke_all_other_service.execute(access_token, current_device)


async def test_revoke_all_other_user_current_session_not_found(
    revoke_all_other_service, mock_session_repo
):
    access_token = "valid-token"
    current_device = "chrome-windows"

    mock_session_repo.get_by_id.side_effect = SessionNotFoundError

    with pytest.raises(SessionNotFoundError):
        await revoke_all_other_service.execute(access_token, current_device)
