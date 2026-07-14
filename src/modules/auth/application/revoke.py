import logging
from src.modules.auth.exceptions import (
    DeviceMismatchError,
    PermissionDenied,
    SessionNotFoundError,
)
from src.modules.auth.domain.ports.session_repo_interface import ISessionRepository
from src.modules.auth.domain.ports.token_decoder_interface import ITokenDecoder
from src.modules.auth.domain.ports.token_encoder_interface import ITokenEncoder
from src.modules.auth.domain.value_objects.user_id import UserID
from src.modules.auth.domain.value_objects.session_id import SessionID
from src.modules.auth.domain.value_objects.device import Device

logger = logging.getLogger(__name__)


class RevokeService:
    def __init__(
        self,
        session_repo: ISessionRepository,
        token_decoder: ITokenDecoder,
        token_encoder: ITokenEncoder,
    ):
        self.session_repo = session_repo
        self.token_decoder = token_decoder
        self.token_encoder = token_encoder

    async def execute(
        self, access_token: str, session_id: str, current_device: str
    ) -> None:
        logger.info("Revoking a session of user: session_id=%s", session_id)
        # Decode token
        payload = self.token_decoder.decode_and_validate(
            field_type_map=self.token_encoder.FIELD_TYPE_MAP,
            token=access_token,
            expected_token_type="access",
        )

        # Extract claims
        user_id = UserID(payload["sub"])
        current_session_id = SessionID(payload["sid"])
        current_session_device = Device(payload["dev"])

        # Check session exists
        try:
            await self.session_repo.get_by_id(current_session_id)
        except SessionNotFoundError as e:
            raise SessionNotFoundError(str(e), "current")

        # Verify device matches session
        if current_session_device.value != current_device:
            raise DeviceMismatchError("Session device mismatch")

        # Retrieve session to delete
        session_to_delete = await self.session_repo.get_by_id(SessionID(session_id))
        # Ensure session belongs to the user
        if session_to_delete.user_id != user_id:
            logger.info(
                "Session did not belong to the user: user_id=%s, session_id=%s",
                user_id.value,
                session_id,
            )
            raise PermissionDenied("Cannot revoke another user's session")
        await self.session_repo.delete(session_id=session_to_delete.id, user_id=user_id)
        logger.debug("session deleted")

        logger.info("Session revoked successfully: session_id=%s", session_id)
