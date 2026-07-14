import pytest
from datetime import datetime, timedelta, timezone
from src.modules.auth.exceptions import DeviceMismatchError, SessionNotFoundError
from src.modules.auth.domain.value_objects.user_id import UserID
from src.modules.auth.domain.value_objects.session_id import SessionID
from src.modules.core.conf import Config


async def test_token_rotation_without_refresh(
    token_rotation_service,
    mock_token_encoder,
    mock_token_decoder,
    mock_session_repo,
):
    # Set exp far in future so no rotation
    mock_token_decoder.decode_and_validate.return_value["exp"] = (
        datetime.now(timezone.utc)
        + timedelta(minutes=Config.ROTATE_THRESHOLD_MINUTES + 100)
    ).timestamp()

    refresh_token = "valid-refresh-token"
    current_device = "chrome-windows"

    new_access, new_refresh = await token_rotation_service.execute(
        refresh_token, current_device
    )

    assert new_access == "access-token"
    assert new_refresh is None
    mock_session_repo.extend_session.assert_not_called()
    mock_token_encoder.create_refresh_token.assert_not_called()


async def test_token_rotation_with_refresh(
    token_rotation_service,
    mock_token_decoder,
    mock_token_encoder,
    mock_session_repo,
):
    # Set exp near expiry to trigger rotation
    mock_token_decoder.decode_and_validate.return_value["exp"] = (
        datetime.now(timezone.utc) + timedelta(minutes=2)
    ).timestamp()

    refresh_token = "valid-refresh-token"
    current_device = "chrome-windows"

    # Mock Config.ROTATE_THRESHOLD_MINUTES
    original_threshold = Config.ROTATE_THRESHOLD_MINUTES
    Config.ROTATE_THRESHOLD_MINUTES = 5

    try:
        new_access, new_refresh = await token_rotation_service.execute(
            refresh_token, current_device
        )
    finally:
        Config.ROTATE_THRESHOLD_MINUTES = original_threshold

    assert new_access == "access-token"
    assert new_refresh == "refresh-token"
    mock_session_repo.extend_session.assert_called_once()
    mock_token_encoder.create_refresh_token.assert_called_once()


async def test_token_rotation_device_mismatch(token_rotation_service):
    refresh_token = "valid-refresh-token"
    current_device = "firefox-linux"

    with pytest.raises(DeviceMismatchError):
        await token_rotation_service.execute(refresh_token, current_device)


async def test_revoke_user_current_session_not_found(
    token_rotation_service, mock_session_repo
):
    refresh_token = "valid-refresh-token"
    current_device = "chrome-windows"

    mock_session_repo.extend_session.side_effect = SessionNotFoundError

    with pytest.raises(SessionNotFoundError):
        await token_rotation_service.execute(refresh_token, current_device)
