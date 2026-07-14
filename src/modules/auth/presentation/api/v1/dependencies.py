from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from functools import lru_cache

from src.modules.core.database import get_async_session
from src.modules.core.redis_client import get_redis_client

from src.modules.auth.domain.ports.user_repo_interface import IUserRepository
from src.modules.auth.domain.ports.session_repo_interface import ISessionRepository
from src.modules.auth.domain.ports.unit_of_work_interface import IUnitOfWork
from src.modules.auth.domain.ports.verification_token_repo_interface import (
    IEmailVerificationTokenRepo,
)
from src.modules.auth.domain.ports.email_sender_interface import IEmailSender
from src.modules.auth.domain.ports.block_email_checker_interface import IEmailChecker
from src.modules.auth.domain.ports.token_decoder_interface import ITokenDecoder
from src.modules.auth.domain.ports.token_encoder_interface import ITokenEncoder
from src.modules.auth.domain.ports.password_hasher_interface import IPasswordHasher

from src.modules.auth.infrastructure.persistence.sqlal_user_repo import (
    SQLAL_UserRepository,
)
from src.modules.auth.infrastructure.persistence.sqlal_unit_of_work import (
    SQLAL_UnitOfWork,
)
from src.modules.auth.infrastructure.cache.redis_session_repo import (
    RedisSessionRepository,
)
from src.modules.auth.infrastructure.cache.redis_verification_token_repo import (
    RedisEmailVerificationTokenRepo,
)
from src.modules.auth.infrastructure.email_sender import ImpEmailSender
from src.modules.auth.infrastructure.security.block_email_checker import ImpEmailChecker
from src.modules.auth.infrastructure.security.jwt_encoder import JWT_TokenEncoder
from src.modules.auth.infrastructure.security.jwt_decoder import JWT_TokenDecoder
from src.modules.auth.infrastructure.security.bcrypt_password_hasher import (
    BcryptPasswordHasher,
)

from src.modules.auth.application.del_account import DelAccountService
from src.modules.auth.application.forget_pass_verify import (
    ForgetPasswordVerificationService,
)
from src.modules.auth.application.login import LoginService
from src.modules.auth.application.logout import LogoutService
from src.modules.auth.application.revoke import RevokeService
from src.modules.auth.application.reset_password import ResetPasswordService
from src.modules.auth.application.revoke_all_other import RevokeAllOtherSessionsService
from src.modules.auth.application.send_verification import SendVerificationService
from src.modules.auth.application.set_password import SetPassService
from src.modules.auth.application.signup import SignupService
from src.modules.auth.application.token_rotation import TokenRotationService

# ============================================================
# BASE DEPENDENCIES
# ============================================================


def get_user_repo(db: AsyncSession = Depends(get_async_session)) -> IUserRepository:
    return SQLAL_UserRepository(db)


def get_session_repo(redis: Redis = Depends(get_redis_client)) -> ISessionRepository:
    return RedisSessionRepository(redis)


def get_verification_token_repo(
    redis: Redis = Depends(get_redis_client),
) -> IEmailVerificationTokenRepo:
    return RedisEmailVerificationTokenRepo(redis)


async def get_uow(
    db: AsyncSession = Depends(get_async_session),
) -> IUnitOfWork:
    return SQLAL_UnitOfWork(db)


@lru_cache(maxsize=1)
def get_token_encoder() -> ITokenEncoder:
    return JWT_TokenEncoder()


@lru_cache(maxsize=1)
def get_token_decoder() -> ITokenDecoder:
    return JWT_TokenDecoder()


@lru_cache(maxsize=1)
def get_password_hasher() -> IPasswordHasher:
    return BcryptPasswordHasher()


@lru_cache(maxsize=1)
def get_email_sender() -> IEmailSender:
    return ImpEmailSender()


@lru_cache(maxsize=1)
def get_email_checker() -> IEmailChecker:
    return ImpEmailChecker()


# ============================================================
# SERVICE DEPENDENCIES
# ============================================================


async def get_del_account_service(
    uow: IUnitOfWork = Depends(get_uow),
    session_repo: ISessionRepository = Depends(get_session_repo),
    token_decoder: ITokenDecoder = Depends(get_token_decoder),
    token_encoder: ITokenEncoder = Depends(get_token_encoder),
) -> DelAccountService:
    return DelAccountService(uow, session_repo, token_decoder, token_encoder)


async def get_forget_pass_service(
    uow: IUnitOfWork = Depends(get_uow),
    token_repo: IEmailVerificationTokenRepo = Depends(get_verification_token_repo),
    email_sender: IEmailSender = Depends(get_email_sender),
) -> ForgetPasswordVerificationService:
    return ForgetPasswordVerificationService(uow, token_repo, email_sender)


async def get_login_service(
    uow: IUnitOfWork = Depends(get_uow),
    session_repo: ISessionRepository = Depends(get_session_repo),
    token_encoder: ITokenEncoder = Depends(get_token_encoder),
    password_hasher: IPasswordHasher = Depends(get_password_hasher),
) -> LoginService:
    return LoginService(uow, session_repo, token_encoder, password_hasher)


async def get_logout_service(
    session_repo: ISessionRepository = Depends(get_session_repo),
    token_decoder: ITokenDecoder = Depends(get_token_decoder),
    token_encoder: ITokenEncoder = Depends(get_token_encoder),
) -> LogoutService:
    return LogoutService(session_repo, token_decoder, token_encoder)


async def get_revoke_service(
    session_repo: ISessionRepository = Depends(get_session_repo),
    token_decoder: ITokenDecoder = Depends(get_token_decoder),
    token_encoder: ITokenEncoder = Depends(get_token_encoder),
) -> RevokeService:
    return RevokeService(session_repo, token_decoder, token_encoder)


async def get_reset_pass_service(
    uow: IUnitOfWork = Depends(get_uow),
    password_hasher: IPasswordHasher = Depends(get_password_hasher),
    token_repo: IEmailVerificationTokenRepo = Depends(get_verification_token_repo),
) -> ResetPasswordService:
    return ResetPasswordService(uow, password_hasher, token_repo)


async def get_revoke_all_other_service(
    session_repo: ISessionRepository = Depends(get_session_repo),
    token_decoder: ITokenDecoder = Depends(get_token_decoder),
    token_encoder: ITokenEncoder = Depends(get_token_encoder),
) -> RevokeAllOtherSessionsService:
    return RevokeAllOtherSessionsService(session_repo, token_decoder, token_encoder)


async def get_send_verification_service(
    token_repo: IEmailVerificationTokenRepo = Depends(get_verification_token_repo),
    email_sender: IEmailSender = Depends(get_email_sender),
    email_checker: IEmailChecker = Depends(get_email_checker),
) -> SendVerificationService:
    return SendVerificationService(token_repo, email_sender, email_checker)


async def get_set_password_service(
    uow: IUnitOfWork = Depends(get_uow),
    session_repo: ISessionRepository = Depends(get_session_repo),
    token_decoder: ITokenDecoder = Depends(get_token_decoder),
    token_encoder: ITokenEncoder = Depends(get_token_encoder),
    password_hasher: IPasswordHasher = Depends(get_password_hasher),
) -> SetPassService:
    return SetPassService(
        uow, session_repo, token_decoder, token_encoder, password_hasher
    )


async def get_signup_service(
    uow: IUnitOfWork = Depends(get_uow),
    session_repo: ISessionRepository = Depends(get_session_repo),
    token_encoder: ITokenEncoder = Depends(get_token_encoder),
    password_hasher: IPasswordHasher = Depends(get_password_hasher),
    token_repo: IEmailVerificationTokenRepo = Depends(get_verification_token_repo),
) -> SignupService:
    return SignupService(uow, session_repo, token_encoder, password_hasher, token_repo)


async def get_token_rotation_service(
    session_repo: ISessionRepository = Depends(get_session_repo),
    token_decoder: ITokenDecoder = Depends(get_token_decoder),
    token_encoder: ITokenEncoder = Depends(get_token_encoder),
) -> TokenRotationService:
    return TokenRotationService(session_repo, token_decoder, token_encoder)
