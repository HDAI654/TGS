import pytest
from src.modules.auth.exceptions import InvalidVerificationToken, DatabaseError
from src.modules.auth.domain.value_objects.email import Email


async def test_signup_success(
    signup_service,
    mock_uow,
    mock_session_repo,
    mock_token_encoder,
    mock_token_repo,
):
    verify_token = "38cffd95-3126-435c-b46b-6a67b8e57607"
    password = "StrongP@ssw0rd"
    current_device = "chrome-windows"

    mock_token_repo.get.return_value = Email("test@example.com")

    access_token, refresh_token = await signup_service.execute(
        verify_token, password, current_device
    )

    mock_token_repo.get.assert_called_once()
    mock_token_repo.delete.assert_called_once()
    mock_uow.users.add.assert_called_once()
    mock_session_repo.add.assert_called_once()
    mock_uow.commit.assert_called_once()
    assert access_token == "access-token"
    assert refresh_token == "refresh-token"


async def test_signup_token_not_found(signup_service, mock_token_repo):
    mock_token_repo.get.return_value = None
    verify_token = "invalid-token"
    password = "StrongP@ssw0rd"
    current_device = "chrome-windows"

    with pytest.raises(InvalidVerificationToken):
        await signup_service.execute(verify_token, password, current_device)


async def test_signup_rollback_on_error(signup_service, mock_uow):
    current_device = "chrome-windows"

    mock_uow.users.add.side_effect = DatabaseError

    with pytest.raises(DatabaseError):
        await signup_service.execute(
            "38cffd95-3126-435c-b46b-6a67b8e57607", "KMeked5245@#$", current_device
        )
