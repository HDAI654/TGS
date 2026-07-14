import pytest
from src.modules.auth.exceptions import (
    DeviceMismatchError,
    DatabaseError,
    SessionNotFoundError,
)
from src.modules.auth.domain.value_objects.user_id import UserID
from src.modules.auth.domain.value_objects.session_id import SessionID


async def test_del_account_success(
    del_acc_service, mock_uow, mock_session_repo, mock_token_decoder
):
    access_token = "valid-token"
    current_device = "chrome-windows"

    await del_acc_service.execute(access_token, current_device)

    mock_uow.users.delete.assert_called_once_with(
        id=UserID("8e89fa33-3f7c-4a98-bcf6-fec97b92dd43")
    )
    mock_session_repo.delete.assert_called_once_with(
        session_id=SessionID("38cffd95-3126-435c-b46b-6a67b8e57607"),
        user_id=UserID("8e89fa33-3f7c-4a98-bcf6-fec97b92dd43"),
    )
    mock_session_repo.delete_all_other_sessions.assert_called_once_with(
        current_session_id=SessionID("38cffd95-3126-435c-b46b-6a67b8e57607"),
        user_id=UserID("8e89fa33-3f7c-4a98-bcf6-fec97b92dd43"),
    )
    mock_uow.commit.assert_called_once()


async def test_del_account_device_mismatch(del_acc_service, mock_token_decoder):
    # Override device in token to cause mismatch
    mock_token_decoder.decode_and_validate.return_value["dev"] = "chrome-windows"
    # Current device is different
    with pytest.raises(DeviceMismatchError):
        await del_acc_service.execute("valid-token", "firefox-linux")


async def test_del_account_rollback_on_error(del_acc_service, mock_uow):
    access_token = "valid-token"
    current_device = "chrome-windows"

    mock_uow.users.delete.side_effect = DatabaseError

    with pytest.raises(DatabaseError):
        await del_acc_service.execute(access_token, current_device)

    mock_uow.rollback.assert_called_once()


async def test_del_account_user_current_session_not_found(
    del_acc_service, mock_session_repo
):
    access_token = "valid-token"
    current_device = "chrome-windows"

    mock_session_repo.delete.side_effect = SessionNotFoundError

    with pytest.raises(SessionNotFoundError):
        await del_acc_service.execute(access_token, current_device)
