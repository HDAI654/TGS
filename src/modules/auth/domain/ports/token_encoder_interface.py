from abc import ABC, abstractmethod
from src.modules.auth.domain.value_objects.user_id import UserID
from src.modules.auth.domain.value_objects.session_id import SessionID
from src.modules.auth.domain.value_objects.device import Device


class ITokenEncoder(ABC):
    FIELD_TYPE_MAP: dict

    @abstractmethod
    def create_access_token(
        self, user_id: UserID, session_id: SessionID, device: Device
    ) -> str:
        """
        Create a short-lived access token for authentication.
        Raises:
            AuthTokenCreationError: Raised when authentication token creation fails.
        """
        pass

    @abstractmethod
    def create_refresh_token(
        self, user_id: UserID, session_id: SessionID, device: Device
    ) -> str:
        """
        Create a long-lived refresh token for obtaining new access tokens.
        Raises:
            AuthTokenCreationError: Raised when authentication token creation fails.
        """
        pass
