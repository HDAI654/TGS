import pytest
from src.modules.auth.exceptions import BlockEmail
from src.modules.auth.domain.value_objects.email import Email


async def test_send_verification_success(
    send_verification_service,
    mock_token_repo,
    mock_email_sender,
    mock_email_checker,
):
    email = "test@example.com"

    await send_verification_service.execute(email)

    mock_email_checker.is_blocked.return_value = False
    mock_email_checker.is_blocked.assert_called_once_with(Email(email))
    mock_token_repo.add.assert_called_once()
    mock_email_sender.send.assert_called_once()
    call_args = mock_email_sender.send.call_args
    assert call_args.kwargs["to"] == Email(email)
    assert "Verify Your Email Address" in call_args.kwargs["subject"]


async def test_send_verification_blocked_email(
    send_verification_service,
    mock_email_checker,
):
    mock_email_checker.is_blocked.return_value = True
    email = "blocked@mailinator.com"

    with pytest.raises(BlockEmail):
        await send_verification_service.execute(email)
