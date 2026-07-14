import logging
from src.modules.auth.domain.ports.user_repo_interface import IUserRepository
from src.modules.auth.domain.entities.user import UserEntity
from src.modules.auth.domain.value_objects.user_id import UserID
from src.modules.auth.domain.value_objects.email import Email
from src.modules.auth.domain.value_objects.hashed_password import HashedPassword
from src.modules.auth.infrastructure.persistence.models import UserModel
from src.modules.auth.exceptions import (
    NoChangesError,
    UserNotFoundError,
    UserDuplicateError,
    DatabaseOperationError,
    DatabaseConnectionError,
    DatabaseTimeoutError,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update, select, exists, delete
from sqlalchemy.exc import (
    IntegrityError,
    OperationalError,
    TimeoutError,
    SQLAlchemyError,
)

logger = logging.getLogger(__name__)


class SQLAL_UserRepository(IUserRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def add(self, user: UserEntity) -> None:
        logger.info(
            "Adding user: public_id=%s, email=%s", user.id.value, user.email.value
        )

        if await self.exists_by_email(user.email):
            logger.debug(
                "Another user already uses this email: public_id=%s, email=%s",
                user.id.value,
                user.email.value,
            )
            raise UserDuplicateError(
                f"Another user already uses this email: {user.email.value!r}"
            )

        user_model = UserModel(
            public_id=user.id.value,
            email=user.email.value,
            hashed_password=user.hashed_password.value,
        )

        self._session.add(user_model)
        await self._execute_db_operation("add_user", self._session.flush)

        logger.info("User added successfully: public_id=%s", user.id.value)

    async def update(
        self, id: UserID, new_password: HashedPassword = None, new_email: Email = None
    ) -> None:
        logger.info(
            "Updating user: public_id=%s, new_password=%s, new_email=%s",
            id.value,
            new_password.value if new_password is not None else None,
            new_email.value if new_email is not None else None,
        )

        update_data = {}
        if new_password is not None:
            update_data["hashed_password"] = new_password.value
        if new_email is not None:
            update_data["email"] = new_email.value

        if not update_data:
            logger.debug("No change to do")
            raise NoChangesError("No non-null changes provided.")

        if new_email is not None and await self.exists_by_email(new_email):
            logger.debug(
                "Another user already uses this email: new_email=%s", new_email.value
            )
            raise UserDuplicateError(
                f"Another user already uses this email: {new_email.value!r}"
            )

        result = await self._execute_db_operation(
            "update_user",
            self._session.execute,
            update(UserModel)
            .where(UserModel.public_id == id.value)
            .values(**update_data)
            .returning(UserModel.public_id),
        )

        updated_id = result.scalar_one_or_none()
        if updated_id is None:
            logger.debug("User not found: public_id=%s", id.value)
            raise UserNotFoundError(f"User with id {id.value!r} not found")

        await self._execute_db_operation("update_user", self._session.flush)

        logger.info("User updated successfully: public_id=%s", id.value)

    async def delete(self, id: UserID) -> None:
        logger.info("Deleting user: public_id=%s", id.value)

        result = await self._execute_db_operation(
            "delete_user",
            self._session.execute,
            delete(UserModel).where(UserModel.public_id == id.value),
        )

        if result.rowcount == 0:
            logger.debug("User not found: public_id=%s", id.value)
            raise UserNotFoundError(f"User with id {id.value!r} not found")

        await self._execute_db_operation(
            "delete_user",
            self._session.flush,
        )

        logger.info("User deleted successfully: public_id=%s", id.value)

    async def get_by_id(self, id: UserID) -> UserEntity:
        logger.info("Start getting user: public_id=%s", id.value)

        result = await self._execute_db_operation(
            "get_by_id",
            self._session.execute,
            select(UserModel).where(UserModel.public_id == id.value),
        )
        user_row = result.scalar_one_or_none()

        if user_row:
            logger.info("User found: public_id=%s", id.value)
            return self._to_entity(user_row)

        logger.debug("User not found: public_id=%s", id.value)

        raise UserNotFoundError(f"User with id {id.value!r} not found")

    async def get_by_email(self, email: Email) -> UserEntity:
        logger.info("Start getting user: email=%s", email.value)

        result = await self._execute_db_operation(
            "get_by_email",
            self._session.execute,
            select(UserModel).where(UserModel.email == email.value),
        )
        user_row = result.scalar_one_or_none()

        if user_row:
            logger.info("User found: email=%s", email.value)
            return self._to_entity(user_row)

        logger.debug("User not found: email=%s", email.value)

        raise UserNotFoundError(f"User with email {email.value!r} not found")

    async def exists_by_id(self, id: UserID) -> bool:
        result = await self._execute_db_operation(
            "exists_user_by_id",
            self._session.execute,
            select(exists().where(UserModel.public_id == id.value)),
        )
        return result.scalar()

    async def exists_by_email(self, email: Email) -> bool:
        result = await self._execute_db_operation(
            "exists_user_by_email",
            self._session.execute,
            select(exists().where(UserModel.email == email.value)),
        )
        return result.scalar()

    def _to_entity(self, user_orm_model: UserModel) -> UserEntity:
        """
        Map SQLAlchemy model → Domain Entity
        """
        return UserEntity.create(
            id=user_orm_model.public_id,
            email=user_orm_model.email,
            hashed_password=user_orm_model.hashed_password,
        )

    async def _execute_db_operation(self, operation: str, coro, *args, **kwargs):
        """Generic wrapper for database operations with error handling"""
        try:
            return await coro(*args, **kwargs)
        except IntegrityError as e:
            logger.exception(f"Database integrity error during {operation}")
            if "duplicate" in str(e).lower() or "unique" in str(e).lower():
                raise UserDuplicateError("User with this email already exists") from e
            raise DatabaseOperationError(f"Database integrity error: {e}") from e
        except OperationalError as e:
            logger.exception(f"Database connection error during {operation}")
            raise DatabaseConnectionError(f"Failed to connect to database: {e}") from e
        except TimeoutError as e:
            logger.exception(f"Database timeout during {operation}")
            raise DatabaseTimeoutError(f"Database operation timed out: {e}") from e
        except SQLAlchemyError as e:
            logger.exception(f"Database error during {operation}")
            raise DatabaseOperationError(f"Database operation failed: {e}") from e
