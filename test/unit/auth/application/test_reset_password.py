import pytest
from src.modules.auth.exceptions import InvalidVerificationToken, DatabaseError
from src.modules.auth.domain.value_objects.email import Email


async def test_reset_pass_success(
    reset_pass_service,
    mock_uow,
    mock_token_repo,
):
    verify_token = "38cffd95-3126-435c-b46b-6a67b8e57607"
    password = "StrongP@ssw0rd"

    mock_token_repo.get.return_value = Email("test@example.com")

    await reset_pass_service.execute(verify_token, password)

    mock_token_repo.get.assert_called_once()
    mock_token_repo.delete.assert_called_once()
    mock_uow.users.update.assert_called_once()
    mock_uow.commit.assert_called_once()


async def test_reset_pass_token_not_found(reset_pass_service, mock_token_repo):
    mock_token_repo.get.return_value = None
    verify_token = "invalid-token"
    password = "StrongP@ssw0rd"

    with pytest.raises(InvalidVerificationToken):
        await reset_pass_service.execute(verify_token, password)


async def test_reset_pass_rollback_on_error(reset_pass_service, mock_uow):
    current_device = "chrome-windows"

    mock_uow.users.update.side_effect = DatabaseError

    with pytest.raises(DatabaseError):
        await reset_pass_service.execute(
            "38cffd95-3126-435c-b46b-6a67b8e57607", "KMeked5245@#$"
        )
