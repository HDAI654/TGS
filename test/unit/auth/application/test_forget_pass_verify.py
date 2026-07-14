import pytest
from src.modules.auth.exceptions import UserNotFoundError
from src.modules.auth.domain.value_objects.email import Email


async def test_forget_pass_success(
    forget_pass_verify_service,
    mock_token_repo,
    mock_email_sender,
):
    email = "test@example.com"

    await forget_pass_verify_service.execute(email)

    mock_token_repo.add.assert_called_once()
    mock_email_sender.send.assert_called_once()
    call_args = mock_email_sender.send.call_args
    assert call_args.kwargs["to"] == Email(email)
    assert "reset" in str(call_args.kwargs["subject"]).lower()


async def test_forget_pass_user_not_exist(
    forget_pass_verify_service,
    mock_uow,
):
    mock_uow.users.exists_by_email.return_value = False
    email = "blocked@mailinator.com"

    with pytest.raises(UserNotFoundError):
        await forget_pass_verify_service.execute(email)
