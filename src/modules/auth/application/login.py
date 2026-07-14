import logging
from src.modules.auth.domain.ports.session_repo_interface import ISessionRepository
from src.modules.auth.domain.ports.unit_of_work_interface import IUnitOfWork
from src.modules.auth.domain.entities.session import SessionEntity
from src.modules.auth.domain.value_objects.email import Email
from src.modules.auth.domain.value_objects.password import Password
from src.modules.auth.domain.ports.token_encoder_interface import ITokenEncoder
from src.modules.auth.domain.ports.password_hasher_interface import IPasswordHasher
from src.modules.auth.exceptions import (
    InvalidEmailOrPassword,
    WeakPasswordError,
    InvalidPasswordError,
)

logger = logging.getLogger(__name__)


class LoginService:
    def __init__(
        self,
        uow: IUnitOfWork,
        session_repo: ISessionRepository,
        token_encoder: ITokenEncoder,
        password_hasher: IPasswordHasher,
    ):
        self.uow = uow
        self.session_repo = session_repo
        self.token_encoder = token_encoder
        self.password_hasher = password_hasher

    async def execute(
        self, email: str, password: str, current_device: str
    ) -> tuple[str, str]:
        logger.info("Logging in user: email=%s", email)

        # Retrieve user by email
        user_email_vo = Email(email)
        user = await self.uow.users.get_by_email(email=user_email_vo)
        logger.debug("User found.")

        # Verify password
        try:
            password_vo = Password(password)
        except (InvalidPasswordError, WeakPasswordError):
            raise InvalidEmailOrPassword()
        if not self.password_hasher.verify(password_vo, user.hashed_password):
            raise InvalidEmailOrPassword()
        logger.debug("Password verified.")

        # Create new session for the authenticated user
        session = SessionEntity.create(user_id=user.id.value, device=current_device)
        await self.session_repo.add(session)
        logger.debug("Session created.")

        # Generate access and refresh tokens
        access_token = self.token_encoder.create_access_token(
            user.id, session.id, session.device
        )
        refresh_token = self.token_encoder.create_refresh_token(
            user.id, session.id, session.device
        )

        logger.info("User logged in successfully: email=%s", email)

        return access_token, refresh_token
