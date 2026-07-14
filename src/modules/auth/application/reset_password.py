import logging
from src.modules.auth.exceptions import (
    InvalidEmailVerificationTokenError,
    InvalidVerificationToken,
)
from src.modules.auth.domain.ports.unit_of_work_interface import IUnitOfWork
from src.modules.auth.domain.ports.password_hasher_interface import IPasswordHasher
from src.modules.auth.domain.ports.verification_token_repo_interface import (
    IEmailVerificationTokenRepo,
)
from src.modules.auth.domain.value_objects.email_verification_token import (
    EmailVerificationToken,
)
from src.modules.auth.domain.value_objects.password import Password

logger = logging.getLogger(__name__)


class ResetPasswordService:
    def __init__(
        self,
        uow: IUnitOfWork,
        password_hasher: IPasswordHasher,
        token_repo: IEmailVerificationTokenRepo,
    ):
        self.uow = uow
        self.password_hasher = password_hasher
        self.token_repo = token_repo

    async def execute(self, verify_token: str, new_password: str) -> None:
        logger.info("Reseting user password")

        try:
            # Check verify token
            try:
                verify_token_vo = EmailVerificationToken(verify_token)
            except InvalidEmailVerificationTokenError:
                raise InvalidVerificationToken(f"Token '{verify_token}' not found")

            # Get email from token
            email_vo = await self.token_repo.get(
                token=verify_token_vo,
                token_type="forget_pass_verify",
            )

            if email_vo is None:
                logger.debug("verifytoken was invalid")
                raise InvalidVerificationToken(f"Token '{verify_token}' not found")

            logger.debug("verifytoken extracted")

            # Delete used token
            await self.token_repo.delete(
                token=verify_token_vo,
                token_type="forget_pass_verify",
            )
            logger.debug("verifytoken deleted")

            # Validate password
            new_password_vo = Password(new_password)

            # Hash the password
            hashed_password = self.password_hasher.hash(new_password_vo)

            # Create new user
            user = await self.uow.users.get_by_email(email_vo)
            await self.uow.users.update(user.id, new_password=hashed_password)
            logger.debug("Password updated")

            # Persist all changes to the database.
            await self.uow.commit()
        except Exception:
            # Rollback all changes.
            await self.uow.rollback()
            raise

        logger.info(
            "User password reset successfully: user_id=%s, email=%s",
            user.email.value,
            user.id.value,
        )
