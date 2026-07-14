import logging
from datetime import timedelta, datetime, timezone
from src.modules.auth.exceptions import DeviceMismatchError
from src.modules.auth.domain.ports.session_repo_interface import ISessionRepository
from src.modules.auth.domain.ports.token_decoder_interface import ITokenDecoder
from src.modules.auth.domain.ports.token_encoder_interface import ITokenEncoder
from src.modules.auth.domain.value_objects.user_id import UserID
from src.modules.auth.domain.value_objects.session_id import SessionID
from src.modules.auth.domain.value_objects.device import Device
from src.modules.core.conf import Config

logger = logging.getLogger(__name__)


class TokenRotationService:
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
        self, refresh_token: str, current_device: str
    ) -> tuple[str, str | None]:
        logger.info("Creating new tokens for user")
        # Decode token
        payload = self.token_decoder.decode_and_validate(
            field_type_map=self.token_encoder.FIELD_TYPE_MAP,
            token=refresh_token,
            expected_token_type="refresh",
        )
        exp: float = payload["exp"]

        # Extract claims
        user_id = UserID(payload["sub"])
        session_id = SessionID(payload["sid"])
        session_device = Device(payload["dev"])

        # Verify device matches session
        if session_device.value != current_device:
            raise DeviceMismatchError("Session device mismatch")

        # Generate new access token
        new_access = self.token_encoder.create_access_token(
            user_id, session_id, session_device
        )

        # Check if refresh token rotation is needed
        try:
            rotate_threshold = timedelta(minutes=Config.ROTATE_THRESHOLD_MINUTES)
            exp = datetime.fromtimestamp(exp, timezone.utc)
            now = datetime.now(timezone.utc)
            need = exp - now <= rotate_threshold
        except Exception as e:
            need = False
        if need:
            # Extend session lifetime
            await self.session_repo.extend_session(session_id)

            # Generate new refresh token
            new_refresh = self.token_encoder.create_refresh_token(
                user_id, session_id, session_device
            )
            logger.info("Both tokens created successfully: user_id=%s", user_id.value)
            return new_access, new_refresh

        logger.info("access-token created successfully: user_id=%s", user_id.value)
        return new_access, None
