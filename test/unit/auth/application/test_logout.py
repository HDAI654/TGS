import pytest
from src.modules.auth.exceptions import DeviceMismatchError, SessionNotFoundError
from src.modules.auth.domain.value_objects.session_id import SessionID
from src.modules.auth.domain.value_objects.user_id import UserID


async def test_logout_success(logout_service, mock_session_repo):
    access_token = "valid-token"
    current_device = "chrome-windows"

    await logout_service.execute(access_token, current_device)

    mock_session_repo.delete.assert_called_once_with(
        session_id=SessionID("38cffd95-3126-435c-b46b-6a67b8e57607"),
        user_id=UserID("8e89fa33-3f7c-4a98-bcf6-fec97b92dd43"),
    )


async def test_logout_device_mismatch(logout_service):
    access_token = "valid-token"
    current_device = "firefox-linux"

    with pytest.raises(DeviceMismatchError):
        await logout_service.execute(access_token, current_device)


async def test_logout_user_current_session_not_found(logout_service, mock_session_repo):
    access_token = "valid-token"
    current_device = "chrome-windows"

    mock_session_repo.delete.side_effect = SessionNotFoundError

    with pytest.raises(SessionNotFoundError):
        await logout_service.execute(access_token, current_device)
