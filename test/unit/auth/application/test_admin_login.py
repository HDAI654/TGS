import pytest
from src.modules.auth.exceptions import InvalidEmailOrPassword
from src.modules.auth.domain.value_objects.email import Email


async def test_admin_login_success(
    admin_login_service,
    mock_uow,
    mock_session_repo,
    mock_token_encoder,
    mock_user_entity,
):
    mock_uow.users.get_by_email.return_value = mock_user_entity

    access_token, refresh_token = await admin_login_service.execute(
        email="test@example.com",
        password="StrongP@ssw0rd",
        current_device="chrome-windows",
        admin_password="efiEKNMEDKehfe4128520efwiuf#$#$&jfecw5ef",
    )

    mock_uow.users.get_by_email.assert_called_once_with(email=Email("test@example.com"))
    assert access_token == "access-token"
    assert refresh_token == "refresh-token"
    mock_session_repo.add.assert_called_once()
    mock_token_encoder.create_access_token.assert_called_once()
    mock_token_encoder.create_refresh_token.assert_called_once()


async def test_admin_login_invalid_password(
    admin_login_service,
    mock_uow,
    mock_user_entity,
    mock_password_hasher,
):
    mock_uow.users.get_by_email.return_value = mock_user_entity
    mock_password_hasher.verify.return_value = False

    with pytest.raises(InvalidEmailOrPassword):
        await admin_login_service.execute(
            email="test@example.com",
            password="wrong",
            current_device="chrome-windows",
            admin_password="efijEKNMEDKe4128520efwiuf#$#$&wujfecw5ef",
        )


async def test_admin_login_weak_password(admin_login_service, mock_uow):
    with pytest.raises(InvalidEmailOrPassword):
        await admin_login_service.execute(
            email="test@example.com",
            password="weak",
            current_device="chrome-windows",
            admin_password="efiwEKNMEDKehfe4128520efwiuf#$#$&fecw5ef",
        )
