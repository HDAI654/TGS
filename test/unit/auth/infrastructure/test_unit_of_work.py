import pytest
from sqlalchemy.exc import (
    OperationalError,
)
from src.modules.auth.infrastructure.persistence.sqlal_unit_of_work import (
    SQLAL_UnitOfWork,
)
from src.modules.core.database import Base
from src.modules.auth.domain.entities.user import UserEntity
from src.modules.auth.domain.value_objects.user_id import UserID
from src.modules.auth.domain.value_objects.session_id import SessionID
from src.modules.auth.domain.value_objects.email import Email
from src.modules.auth.domain.value_objects.hashed_password import HashedPassword
from src.modules.auth.exceptions import (
    DatabaseConnectionError,
)


class TestUnitOfWork:
    @pytest.fixture
    async def uow(self, db_session):
        return SQLAL_UnitOfWork(db_session)

    @pytest.fixture
    async def sample_user(self):
        return UserEntity(
            id=UserID.generate(),
            email=Email("test@example.com"),
            hashed_password=HashedPassword("hashed_password_123"),
        )

    async def test_commit_successfully(self, uow, sample_user):
        await uow.users.add(sample_user)
        await uow.commit()

        # Verify user was actually saved
        saved_user = await uow.users.get_by_email(sample_user.email)
        assert saved_user.id.value == sample_user.id.value
        assert saved_user.email.value == sample_user.email.value

    async def test_commit_rollback_on_error(self, uow, sample_user, mocker):
        mocker.patch.object(
            uow._session,
            "flush",
            side_effect=lambda: None,
        )

        # Add a user
        await uow.users.add(sample_user)

        mocker.patch.object(
            uow._session,
            "commit",
            side_effect=OperationalError("statement", "params", "orig"),
        )

        # Mock rollback to track call
        mock_rollback = mocker.patch.object(uow._session, "rollback")

        with pytest.raises(DatabaseConnectionError):
            await uow.commit()

        # Rollback should have been called
        uow._session.rollback.assert_called_once()

        # Verify the user wasn't saved
        assert await uow.users.exists_by_id(sample_user.id) is False

    async def test_commit_with_no_changes(self, uow):
        # Should not raise any error
        await uow.commit()

    async def test_rollback_discards_changes(self, uow, sample_user):
        await uow.users.add(sample_user)

        # Rollback before commit
        await uow.rollback()

        # User should not exist in database
        exists = await uow.users.exists_by_email(sample_user.email)
        assert exists is False

    async def test_multiple_operations_in_one_transaction(self, uow):
        user1 = UserEntity(
            id=UserID.generate(),
            email=Email("user1@example.com"),
            hashed_password=HashedPassword("pass1"),
        )
        user2 = UserEntity(
            id=UserID.generate(),
            email=Email("user2@example.com"),
            hashed_password=HashedPassword("pass2"),
        )

        await uow.users.add(user1)
        await uow.users.add(user2)
        await uow.commit()

        # Both should be saved
        assert await uow.users.exists_by_email(user1.email) is True
        assert await uow.users.exists_by_email(user2.email) is True

    async def test_rollback_after_multiple_operations(self, uow):
        user1 = UserEntity(
            id=UserID.generate(),
            email=Email("user1@example.com"),
            hashed_password=HashedPassword("pass1"),
        )
        user2 = UserEntity(
            id=UserID.generate(),
            email=Email("user2@example.com"),
            hashed_password=HashedPassword("pass2"),
        )

        await uow.users.add(user1)
        await uow.users.add(user2)
        await uow.rollback()

        # Neither should be saved
        assert await uow.users.exists_by_email(user1.email) is False
        assert await uow.users.exists_by_email(user2.email) is False

    async def test_commit_after_rollback(self, uow, sample_user):
        await uow.users.add(sample_user)
        await uow.rollback()

        # Add again after rollback
        await uow.users.add(sample_user)
        await uow.commit()

        assert await uow.users.exists_by_email(sample_user.email) is True
