from abc import ABC, abstractmethod
from src.modules.auth.domain.entities.user import UserEntity
from src.modules.auth.domain.value_objects.user_id import UserID
from src.modules.auth.domain.value_objects.email import Email
from src.modules.auth.domain.value_objects.hashed_password import HashedPassword


class IUserRepository(ABC):
    """Repository interface for User entities."""

    @abstractmethod
    async def add(self, user: UserEntity) -> None:
        """
        Create a new user in the database.
        Raises:
            DatabaseConnectionError: Raised when cannot connect to database.
            DatabaseTimeoutError: Raised when database operation times out.
            DatabaseOperationError: Raised when database operation fails.
        """
        pass

    @abstractmethod
    async def update(
        self, id: UserID, new_password: HashedPassword = None, new_email: Email = None
    ) -> None:
        """
        Update an existing user in the database.
        Raises:
            DatabaseConnectionError: Raised when cannot connect to database.
            DatabaseTimeoutError: Raised when database operation times out.
            DatabaseOperationError: Raised when database operation fails.
            NoChangesError: No changes provided for update.
            InvalidFieldError: Invalid field provided for update.
            UserNotFoundError: Raised when User not found.
        """
        pass

    @abstractmethod
    async def delete(self, id: UserID) -> None:
        """
        Delete a user by UserID.
        Raises:
            DatabaseConnectionError: Raised when cannot connect to database.
            DatabaseTimeoutError: Raised when database operation times out.
            DatabaseOperationError: Raised when database operation fails.
            UserNotFoundError: Raised when User not found.
        """
        pass

    @abstractmethod
    async def get_by_id(self, id: UserID) -> UserEntity:
        """
        Get a user by UserID.
        Raises:
            DatabaseConnectionError: Raised when cannot connect to database.
            DatabaseTimeoutError: Raised when database operation times out.
            DatabaseOperationError: Raised when database operation fails.
            UserNotFoundError: Raised when User not found.
        """
        pass

    @abstractmethod
    async def get_by_email(self, email: Email) -> UserEntity:
        """
        Get a user by email.
        Raises:
            DatabaseConnectionError: Raised when cannot connect to database.
            DatabaseTimeoutError: Raised when database operation times out.
            DatabaseOperationError: Raised when database operation fails.
            UserNotFoundError: Raised when User not found.
        """
        pass

    @abstractmethod
    async def exists_by_id(self, id: UserID) -> bool:
        """
        Check if a user exists by UserID.
        Raises:
            DatabaseConnectionError: Raised when cannot connect to database.
            DatabaseTimeoutError: Raised when database operation times out.
            DatabaseOperationError: Raised when database operation fails.
        """
        pass

    @abstractmethod
    async def exists_by_email(self, email: Email) -> bool:
        """
        Check if a user exists by email.
        Raises:
            DatabaseConnectionError: Raised when cannot connect to database.
            DatabaseTimeoutError: Raised when database operation times out.
            DatabaseOperationError: Raised when database operation fails.
        """
        pass
