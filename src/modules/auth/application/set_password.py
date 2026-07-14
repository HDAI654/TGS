import logging
from src.modules.auth.exceptions import DeviceMismatchError
from src.modules.auth.domain.ports.session_repo_interface import ISessionRepository
from src.modules.auth.domain.ports.unit_of_work_interface import IUnitOfWork
from src.modules.auth.domain.ports.token_decoder_interface import ITokenDecoder
from src.modules.auth.domain.ports.token_encoder_interface import ITokenEncoder
from src.modules.auth.domain.ports.password_hasher_interface import IPasswordHasher
from src.modules.auth.domain.value_objects.user_id import UserID
from src.modules.auth.domain.value_objects.session_id import SessionID
from src.modules.auth.domain.value_objects.device import Device
from src.modules.auth.domain.value_objects.password import Password

logger = logging.getLogger(__name__)


class SetPassService:
    def __init__(
        self,
        uow: IUnitOfWork,
        session_repo: ISessionRepository,
        token_decoder: ITokenDecoder,
        token_encoder: ITokenEncoder,
        password_hasher: IPasswordHasher,
    ):
        self.uow = uow
        self.session_repo = session_repo
        self.token_decoder = token_decoder
        self.token_encoder = token_encoder
        self.password_hasher = password_hasher

    async def execute(
        self, access_token: str, new_password: str, current_device: str
    ) -> None:
        logger.info("Changing user password")

        try:
            # Decode token
            payload = self.token_decoder.decode_and_validate(
                field_type_map=self.token_encoder.FIELD_TYPE_MAP,
                token=access_token,
                expected_token_type="access",
            )

            # Extract claims
            user_id = UserID(payload["sub"])
            session_id = SessionID(payload["sid"])
            session_device = Device(payload["dev"])

            # Check session exists
            await self.session_repo.get_by_id(session_id)

            # Verify device matches session
            if session_device.value != current_device:
                raise DeviceMismatchError("Session device mismatch")

            # Validate new password
            new_password_vo = Password(new_password)

            # Hash the new password
            new_hashed_password = self.password_hasher.hash(new_password_vo)

            # Update user password
            await self.uow.users.update(id=user_id, new_password=new_hashed_password)
            logger.debug("Password updated")

            # Revoke all other sessions to force re-authentication on other devices
            await self.session_repo.delete_all_other_sessions(
                current_session_id=session_id, user_id=user_id
            )
            logger.debug("All other sessions revoked")

            # Persist all changes to the database.
            await self.uow.commit()
        except Exception:
            # Rollback all changes.
            await self.uow.rollback()
            raise

        logger.info("User password changed successfully: user_id=%s", user_id.value)
