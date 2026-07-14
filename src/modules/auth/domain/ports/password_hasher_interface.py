from abc import ABC, abstractmethod
from src.modules.auth.domain.value_objects.password import Password
from src.modules.auth.domain.value_objects.hashed_password import HashedPassword


class IPasswordHasher(ABC):
    """Interface for password hashing."""

    @abstractmethod
    def hash(self, password: Password) -> HashedPassword:
        """Hash a plain password."""
        pass

    @abstractmethod
    def verify(self, plain: Password, hashed: HashedPassword) -> bool:
        """Verify a password against a hash."""
        pass
