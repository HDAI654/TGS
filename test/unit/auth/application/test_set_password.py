import pytest
from src.modules.auth.exceptions import (
    DeviceMismatchError,
    SessionNotFoundError,
    DatabaseError,
)
from src.modules.auth.domain.value_objects.user_id import UserID
from src.modules.auth.domain.value_objects.session_id import SessionID


async def test_set_password_success(
    set_pass_service,
    mock_uow,
    mock_session_repo,
    mock_password_hasher,
):
    access_token = "valid-token"
    new_password = "NewStrongP@ssw0rd"
    current_device = "chrome-windows"

    await set_pass_service.execute(access_token, new_password, current_device)

    mock_uow.users.update.assert_called_once()
    mock_session_repo.delete_all_other_sessions.assert_called_once_with(
        current_session_id=SessionID("38cffd95-3126-435c-b46b-6a67b8e57607"),
        user_id=UserID("8e89fa33-3f7c-4a98-bcf6-fec97b92dd43"),
    )
    mock_uow.commit.assert_called_once()


async def test_set_password_device_mismatch(set_pass_service):
    access_token = "valid-token"
    new_password = "NewStrongP@ssw0rd"
    current_device = "firefox-linux"

    with pytest.raises(DeviceMismatchError):
        await set_pass_service.execute(access_token, new_password, current_device)


async def test_set_password_rollback_on_error(set_pass_service, mock_uow):
    access_token = "valid-token"
    current_device = "chrome-windows"

    mock_uow.users.update.side_effect = DatabaseError

    with pytest.raises(DatabaseError):
        await set_pass_service.execute(access_token, "KMeked5245@#$", current_device)

    mock_uow.rollback.assert_called_once()


async def test_set_password_user_current_session_not_found(
    set_pass_service, mock_session_repo
):
    access_token = "valid-token"
    current_device = "chrome-windows"

    mock_session_repo.get_by_id.side_effect = SessionNotFoundError

    with pytest.raises(SessionNotFoundError):
        await set_pass_service.execute(access_token, "KMeked5245@#$", current_device)
