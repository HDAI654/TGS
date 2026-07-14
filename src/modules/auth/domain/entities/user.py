from src.modules.core.entity import Entity
from src.modules.auth.domain.value_objects.user_id import UserID
from src.modules.auth.domain.value_objects.email import Email
from src.modules.auth.domain.value_objects.hashed_password import HashedPassword


class UserEntity(Entity):
    def __init__(
        self,
        id: UserID,
        email: Email,
        hashed_password: HashedPassword,
    ):
        self.id = id
        self.email = email
        self.hashed_password = hashed_password

        super().__init__()

    @classmethod
    def create(
        cls,
        email: str,
        hashed_password: str,
        id: str | None = None,
    ) -> "UserEntity":
        """Create a new UserEntity."""

        return cls(
            id=UserID(id) if id is not None else UserID.generate(),
            email=Email(email),
            hashed_password=HashedPassword(hashed_password),
        )
