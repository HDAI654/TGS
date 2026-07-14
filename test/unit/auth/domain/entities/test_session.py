import uuid
from src.modules.auth.domain.entities.session import SessionEntity
from src.modules.auth.domain.value_objects.session_id import SessionID
from src.modules.auth.domain.value_objects.user_id import UserID
from src.modules.auth.domain.value_objects.device import Device
from src.modules.auth.domain.value_objects.date import Date


class TestSessionEntity:
    def test_create_success(self):
        id = str(uuid.uuid4())
        user_id = str(uuid.uuid4())
        device = "Android"
        created_at = "2026-07-07"

        session = SessionEntity.create(
            id=id,
            user_id=user_id,
            device=device,
            created_at=created_at,
        )

        assert isinstance(session.id, SessionID)
        assert session.id.value == id
        assert isinstance(session.user_id, UserID)
        assert session.user_id.value == user_id
        assert isinstance(session.device, Device)
        assert session.device.value == device
        assert isinstance(session.created_at, Date)
        assert session.created_at.value.isoformat() == created_at

    def test_create_with_vos(self):
        id = SessionID(str(uuid.uuid4()))
        user_id = UserID(str(uuid.uuid4()))
        device = Device("Android")
        created_at = Date("2026-07-07")

        session = SessionEntity(
            id=id,
            user_id=user_id,
            device=device,
            created_at=created_at,
        )

        assert isinstance(session.id, SessionID)
        assert session.id == id
        assert isinstance(session.user_id, UserID)
        assert session.user_id == user_id
        assert isinstance(session.device, Device)
        assert session.device == device
        assert isinstance(session.created_at, Date)
        assert session.created_at == created_at

    def test_create_without_id(self):
        id = str(uuid.uuid4())
        user_id = str(uuid.uuid4())
        device = "Android"
        created_at = "2026-07-07"

        session = SessionEntity.create(
            id=id,
            user_id=user_id,
            device=device,
            created_at=created_at,
        )

        assert isinstance(session.id, SessionID)
        assert len(session.id.value) == 36
        assert isinstance(session.user_id, UserID)
        assert session.user_id.value == user_id
        assert isinstance(session.device, Device)
        assert session.device.value == device
        assert isinstance(session.created_at, Date)
        assert session.created_at.value.isoformat() == created_at
