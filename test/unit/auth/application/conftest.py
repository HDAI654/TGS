import pytest
from unittest.mock import AsyncMock, Mock
from datetime import datetime
from src.modules.auth.application.del_account import DelAccountService
from src.modules.auth.application.forget_pass_verify import (
    ForgetPasswordVerificationService,
)
from src.modules.auth.application.login import LoginService
from src.modules.auth.application.logout import LogoutService
from src.modules.auth.application.reset_password import ResetPasswordService
from src.modules.auth.application.revoke import RevokeService
from src.modules.auth.application.revoke_all_other import RevokeAllOtherSessionsService
from src.modules.auth.application.send_verification import SendVerificationService
from src.modules.auth.application.set_password import SetPassService
from src.modules.auth.application.signup import SignupService
from src.modules.auth.application.token_rotation import TokenRotationService

from src.modules.auth.domain.entities.user import UserEntity
from src.modules.auth.domain.entities.session import SessionEntity
from src.modules.auth.domain.value_objects.user_id import UserID
from src.modules.auth.domain.value_objects.session_id import SessionID
from src.modules.auth.domain.value_objects.email import Email
from src.modules.auth.domain.value_objects.hashed_password import HashedPassword
from src.modules.auth.domain.value_objects.device import Device
from src.modules.auth.domain.value_objects.date import Date

# ============================================================
# MOCK REPOSITORIES
# ============================================================


@pytest.fixture
def mock_uow():
    uow = AsyncMock()
    uow.users = AsyncMock()
    return uow


@pytest.fixture
def mock_session_repo():
    return AsyncMock()


@pytest.fixture
def mock_token_decoder():
    decoder = Mock()
    decoder.decode_and_validate.return_value = {
        "sub": "8e89fa33-3f7c-4a98-bcf6-fec97b92dd43",
        "sid": "38cffd95-3126-435c-b46b-6a67b8e57607",
        "dev": "chrome-windows",
        "exp": 1735689600.0,
    }
    return decoder


@pytest.fixture
def mock_token_encoder():
    encoder = Mock()
    encoder.FIELD_TYPE_MAP = {}
    encoder.create_access_token.return_value = "access-token"
    encoder.create_refresh_token.return_value = "refresh-token"
    return encoder


@pytest.fixture
def mock_password_hasher():
    hasher = Mock()
    hasher.hash.return_value = HashedPassword("hashed-password")
    hasher.verify.return_value = True
    return hasher


@pytest.fixture
def mock_token_repo():
    repo = AsyncMock()
    repo.get.return_value = Email("test@example.com")
    return repo


@pytest.fixture
def mock_email_sender():
    return AsyncMock()


@pytest.fixture
def mock_email_checker():
    checker = AsyncMock()
    checker.is_blocked.return_value = False
    return checker


# ============================================================
# MOCK ENTITIES
# ============================================================


@pytest.fixture
def mock_user_entity():
    return UserEntity(
        id=UserID("8e89fa33-3f7c-4a98-bcf6-fec97b92dd43"),
        email=Email("test@example.com"),
        hashed_password=HashedPassword("hashed-password"),
    )


@pytest.fixture
def mock_session_entity():
    return SessionEntity(
        id=SessionID("38cffd95-3126-435c-b46b-6a67b8e57607"),
        user_id=UserID("8e89fa33-3f7c-4a98-bcf6-fec97b92dd43"),
        device=Device("chrome-windows"),
        created_at=Date("2026-07-07"),
    )


@pytest.fixture
def mock_other_session_entity():
    return SessionEntity(
        id=SessionID("a1b2c3d4-e5f6-7890-abcd-ef1234567890"),
        user_id=UserID("8e89fa33-3f7c-4a98-bcf6-fec97b92dd43"),
        device=Device("firefox-linux"),
        created_at=Date("2026-07-08"),
    )


# ============================================================
# SERVICE FIXTURES
# ============================================================


@pytest.fixture
def del_acc_service(
    mock_uow,
    mock_session_repo,
    mock_token_decoder,
    mock_token_encoder,
):
    return DelAccountService(
        uow=mock_uow,
        session_repo=mock_session_repo,
        token_decoder=mock_token_decoder,
        token_encoder=mock_token_encoder,
    )


@pytest.fixture
def forget_pass_verify_service(
    mock_uow,
    mock_token_repo,
    mock_email_sender,
):
    return ForgetPasswordVerificationService(
        uow=mock_uow,
        token_repo=mock_token_repo,
        email_sender=mock_email_sender,
    )


@pytest.fixture
def login_service(
    mock_uow,
    mock_session_repo,
    mock_token_encoder,
    mock_password_hasher,
):
    return LoginService(
        uow=mock_uow,
        session_repo=mock_session_repo,
        token_encoder=mock_token_encoder,
        password_hasher=mock_password_hasher,
    )


@pytest.fixture
def logout_service(
    mock_session_repo,
    mock_token_decoder,
    mock_token_encoder,
):
    return LogoutService(
        session_repo=mock_session_repo,
        token_decoder=mock_token_decoder,
        token_encoder=mock_token_encoder,
    )


@pytest.fixture
def reset_pass_service(
    mock_uow,
    mock_password_hasher,
    mock_token_repo,
):
    return ResetPasswordService(
        uow=mock_uow,
        password_hasher=mock_password_hasher,
        token_repo=mock_token_repo,
    )


@pytest.fixture
def revoke_service(
    mock_session_repo,
    mock_token_decoder,
    mock_token_encoder,
):
    return RevokeService(
        session_repo=mock_session_repo,
        token_decoder=mock_token_decoder,
        token_encoder=mock_token_encoder,
    )


@pytest.fixture
def revoke_all_other_service(
    mock_session_repo,
    mock_token_decoder,
    mock_token_encoder,
):
    return RevokeAllOtherSessionsService(
        session_repo=mock_session_repo,
        token_decoder=mock_token_decoder,
        token_encoder=mock_token_encoder,
    )


@pytest.fixture
def send_verification_service(
    mock_token_repo,
    mock_email_sender,
    mock_email_checker,
):
    return SendVerificationService(
        token_repo=mock_token_repo,
        email_sender=mock_email_sender,
        email_checker=mock_email_checker,
    )


@pytest.fixture
def set_pass_service(
    mock_uow,
    mock_session_repo,
    mock_token_decoder,
    mock_token_encoder,
    mock_password_hasher,
):
    return SetPassService(
        uow=mock_uow,
        session_repo=mock_session_repo,
        token_decoder=mock_token_decoder,
        token_encoder=mock_token_encoder,
        password_hasher=mock_password_hasher,
    )


@pytest.fixture
def signup_service(
    mock_uow,
    mock_session_repo,
    mock_token_encoder,
    mock_password_hasher,
    mock_token_repo,
):
    return SignupService(
        uow=mock_uow,
        session_repo=mock_session_repo,
        token_encoder=mock_token_encoder,
        password_hasher=mock_password_hasher,
        token_repo=mock_token_repo,
    )


@pytest.fixture
def token_rotation_service(
    mock_session_repo,
    mock_token_decoder,
    mock_token_encoder,
):
    return TokenRotationService(
        session_repo=mock_session_repo,
        token_decoder=mock_token_decoder,
        token_encoder=mock_token_encoder,
    )
