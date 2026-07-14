import uuid
from src.modules.auth.domain.entities.user import UserEntity
from src.modules.auth.domain.value_objects.user_id import UserID
from src.modules.auth.domain.value_objects.email import Email
from src.modules.auth.domain.value_objects.hashed_password import HashedPassword


class TestUserEntity:
    def test_create_success(self):
        user_id = str(uuid.uuid4())
        email = "test@example.com"
        hashed_password = "hashed_password_123"

        user = UserEntity.create(
            id=user_id,
            email=email,
            hashed_password=hashed_password,
        )

        assert isinstance(user.id, UserID)
        assert user.id.value == user_id
        assert isinstance(user.email, Email)
        assert user.email.value == email
        assert isinstance(user.hashed_password, HashedPassword)
        assert user.hashed_password.value == hashed_password

    def test_create_with_vos(self):
        user_id = UserID(str(uuid.uuid4()))
        email = Email("test@example.com")
        hashed_password = HashedPassword("hashed_password_123")

        user = UserEntity(
            id=user_id,
            email=email,
            hashed_password=hashed_password,
        )

        assert isinstance(user.id, UserID)
        assert user.id == user_id
        assert isinstance(user.email, Email)
        assert user.email == email
        assert isinstance(user.hashed_password, HashedPassword)
        assert user.hashed_password == hashed_password

    def test_create_without_id(self):
        email = "test@example.com"
        hashed_password = "hashed_password_123"

        user = UserEntity.create(
            email=email,
            hashed_password=hashed_password,
        )

        assert isinstance(user.id, UserID)
        assert len(user.id.value) == 36
        assert user.email.value == email
        assert user.hashed_password.value == hashed_password
