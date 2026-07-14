from datetime import date
from src.modules.core.entity import Entity
from src.modules.auth.domain.value_objects.session_id import SessionID
from src.modules.auth.domain.value_objects.user_id import UserID
from src.modules.auth.domain.value_objects.date import Date
from src.modules.auth.domain.value_objects.device import Device


class SessionEntity(Entity):
    def __init__(
        self,
        id: SessionID,
        user_id: UserID,
        device: Device,
        created_at: Date,
    ):
        self.id = id
        self.user_id = user_id
        self.device = device
        self.created_at = created_at

        super().__init__()

    @classmethod
    def create(
        cls,
        user_id: str,
        device: str = "unknown",
        id: str | None = None,
        created_at: str | date | None = None,
    ) -> "SessionEntity":
        """Create a new SessionEntity."""

        return cls(
            id=SessionID(id) if id is not None else SessionID.generate(),
            user_id=UserID(user_id),
            device=Device(device),
            created_at=(
                Date(created_at) if created_at is not None else Date(date.today())
            ),
        )
