import logging
from src.modules.auth.exceptions import DeviceMismatchError
from src.modules.auth.domain.ports.session_repo_interface import ISessionRepository
from src.modules.auth.domain.ports.unit_of_work_interface import IUnitOfWork
from src.modules.auth.domain.ports.token_decoder_interface import ITokenDecoder
from src.modules.auth.domain.ports.token_encoder_interface import ITokenEncoder
from src.modules.auth.domain.value_objects.user_id import UserID
from src.modules.auth.domain.value_objects.session_id import SessionID
from src.modules.auth.domain.value_objects.device import Device

logger = logging.getLogger(__name__)


class DelAccountService:
    def __init__(
        self,
        uow: IUnitOfWork,
        session_repo: ISessionRepository,
        token_decoder: ITokenDecoder,
        token_encoder: ITokenEncoder,
    ):
        self.uow = uow
        self.session_repo = session_repo
        self.token_decoder = token_decoder
        self.token_encoder = token_encoder

    async def execute(self, access_token: str, current_device: str) -> None:
        logger.info("Deleting user account")
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

            # Verify device matches session
            if session_device.value != current_device:
                raise DeviceMismatchError("Session device mismatch")

            # Delete the current session
            await self.session_repo.delete(session_id=session_id, user_id=user_id)
            logger.debug("User's current session deleted")

            # Delete user account
            await self.uow.users.delete(id=user_id)
            logger.debug("User deleted: user_id=%s", user_id.value)

            # Delete all other active sessions for this user
            await self.session_repo.delete_all_other_sessions(
                current_session_id=session_id, user_id=user_id
            )
            logger.debug("All user sessions deleted")

            # Persist all changes to the database.
            await self.uow.commit()
        except Exception:
            # Rollback all changes.
            await self.uow.rollback()
            raise

        logger.info("User account deleted successfully: user_id=%s", user_id.value)
