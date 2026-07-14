import logging
from src.modules.auth.exceptions import (
    InvalidEmailVerificationTokenError,
    InvalidVerificationToken,
)
from src.modules.auth.domain.ports.session_repo_interface import ISessionRepository
from src.modules.auth.domain.ports.unit_of_work_interface import IUnitOfWork
from src.modules.auth.domain.ports.token_encoder_interface import ITokenEncoder
from src.modules.auth.domain.ports.password_hasher_interface import IPasswordHasher
from src.modules.auth.domain.ports.verification_token_repo_interface import (
    IEmailVerificationTokenRepo,
)
from src.modules.auth.domain.entities.user import UserEntity
from src.modules.auth.domain.entities.session import SessionEntity
from src.modules.auth.domain.value_objects.email_verification_token import (
    EmailVerificationToken,
)
from src.modules.auth.domain.value_objects.password import Password

logger = logging.getLogger(__name__)


class SignupService:
    def __init__(
        self,
        uow: IUnitOfWork,
        session_repo: ISessionRepository,
        token_encoder: ITokenEncoder,
        password_hasher: IPasswordHasher,
        token_repo: IEmailVerificationTokenRepo,
    ):
        self.uow = uow
        self.session_repo = session_repo
        self.token_encoder = token_encoder
        self.password_hasher = password_hasher
        self.token_repo = token_repo

    async def execute(
        self, verify_token: str, password: str, current_device: str
    ) -> tuple[str, str]:
        logger.info("Signing up user")

        try:
            # Check verify token
            try:
                verify_token_vo = EmailVerificationToken(verify_token)
            except InvalidEmailVerificationTokenError:
                raise InvalidVerificationToken(f"Token '{verify_token}' not found")

            # Get email from token
            email_vo = await self.token_repo.get(
                token=verify_token_vo,
                token_type="verifyemail",
            )

            if email_vo is None:
                logger.debug("verifytoken was invalid")
                raise InvalidVerificationToken(f"Token '{verify_token}' not found")

            logger.debug("Verify token extracted")

            # Delete used token
            await self.token_repo.delete(
                token=verify_token_vo,
                token_type="verifyemail",
            )
            logger.debug("Verify token deleted")

            # Validate password
            password_vo = Password(password)

            # Hash the password
            hashed_password = self.password_hasher.hash(password_vo)

            # Create new user
            user = UserEntity.create(
                email=email_vo.value,
                hashed_password=hashed_password.value,
            )
            await self.uow.users.add(user)
            logger.debug("User created")

            # Create session for the new user
            session = SessionEntity.create(
                user_id=user.id.value,
                device=current_device,
            )
            await self.session_repo.add(session)
            logger.debug("Session created")

            # Generate access and refresh tokens
            access_token = self.token_encoder.create_access_token(
                user.id, session.id, session.device
            )
            refresh_token = self.token_encoder.create_refresh_token(
                user.id, session.id, session.device
            )

            # Persist all changes to the database.
            await self.uow.commit()
        except Exception:
            # Rollback all changes.
            await self.uow.rollback()
            raise

        logger.info(
            "User signed up successfully: user_id=%s, email=%s",
            user.email.value,
            user.id.value,
        )

        return access_token, refresh_token
