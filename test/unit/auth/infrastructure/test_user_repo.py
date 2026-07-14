from src.modules.auth.infrastructure.persistence.sqlal_user_repo import (
    SQLAL_UserRepository,
)
import pytest
from sqlalchemy import select, exists
from src.modules.auth.infrastructure.persistence.models import UserModel
from src.modules.auth.domain.entities.user import UserEntity
from src.modules.auth.exceptions import (
    UserNotFoundError,
    NoChangesError,
    UserDuplicateError,
)
from src.modules.auth.domain.value_objects.user_id import UserID
from src.modules.auth.domain.value_objects.email import Email
from src.modules.auth.domain.value_objects.hashed_password import HashedPassword


class TestUserRepo:
    @pytest.fixture
    async def repo(self, db_session):
        return SQLAL_UserRepository(db_session)

    @pytest.fixture
    async def user_seed(self, db_session):
        user = UserModel(
            public_id=UserID.generate().value,
            email="mynewexampleemail@me.he",
            hashed_password="HashedPassword",
        )
        db_session.add(user)
        await db_session.flush()
        return user

    @pytest.fixture
    async def second_user_seed(self, db_session):
        user = UserModel(
            public_id=UserID.generate().value,
            email="myanothernewexampleemail@me.he",
            hashed_password="NewHashedPassword",
        )
        db_session.add(user)
        await db_session.flush()
        return user

    @pytest.fixture
    async def user_entity(self, user_seed):
        return UserEntity.create(
            id=user_seed.public_id,
            email=user_seed.email,
            hashed_password=user_seed.hashed_password,
        )

    @pytest.fixture
    async def non_existent_user_entity(self, user_seed):
        return UserEntity.create(
            id=UserID.generate().value,
            email="differentemail@dfr.gmail",
            hashed_password="supersecretpassword",
        )

    async def test_gets(self, repo, user_entity):
        assert await repo.get_by_id(user_entity.id) == user_entity
        assert await repo.get_by_email(user_entity.email) == user_entity

    async def test_gets_with_non_existent_user(self, repo, non_existent_user_entity):
        with pytest.raises(UserNotFoundError):
            await repo.get_by_id(non_existent_user_entity.id)
            await repo.get_by_email(non_existent_user_entity.email)

    async def test_exists(self, repo, user_entity):
        assert await repo.exists_by_id(user_entity.id) == True
        assert await repo.exists_by_email(user_entity.email) == True

    async def test_exists_with_non_existent_user(self, repo, non_existent_user_entity):
        assert await repo.exists_by_id(non_existent_user_entity.id) == False
        assert await repo.exists_by_email(non_existent_user_entity.email) == False

    ########### Tests of update() ###########
    async def test_update_single_field_successfully(
        self, repo, db_session, user_entity
    ):
        await repo.update(
            id=user_entity.id,
            new_email=Email("slimshady@eminem.em"),
        )

        result = await db_session.execute(
            select(UserModel).where(UserModel.public_id == user_entity.id.value)
        )
        updated_user = result.scalar_one()

        assert updated_user.email == "slimshady@eminem.em"
        assert updated_user.hashed_password == user_entity.hashed_password.value

    async def test_update_multiple_fields_successfully(
        self, repo, db_session, user_entity
    ):
        await repo.update(
            id=user_entity.id,
            new_email=Email("slimshady@eminem.em"),
            new_password=HashedPassword("newhashedpassword"),
        )

        result = await db_session.execute(
            select(UserModel).where(UserModel.public_id == user_entity.id.value)
        )
        updated_user = result.scalar_one()

        assert updated_user.email == "slimshady@eminem.em"
        assert updated_user.hashed_password == "newhashedpassword"

    async def test_update_raises_when_user_not_found(self, repo):
        with pytest.raises(UserNotFoundError):
            await repo.update(
                UserID.generate(),
                new_email=Email("slimshady@eminem.em"),
            )

    async def test_update_raises_when_no_fields_provided(self, repo, user_seed):
        user_id = UserID(user_seed.public_id)

        with pytest.raises(NoChangesError):
            await repo.update(user_id)
            await repo.update(user_id, None, None)

    async def test_update_raises_when_username_already_exists(
        self, repo, user_entity, second_user_seed
    ):

        with pytest.raises(UserDuplicateError):
            await repo.update(
                user_entity.id,
                new_email=Email(second_user_seed.email),
            )

    async def test_delete(self, repo, user_entity, db_session):
        await repo.delete(user_entity.id)

        result = await db_session.execute(
            select(exists().where(UserModel.public_id == user_entity.id.value))
        )
        result = result.scalar()
        assert result is False

    async def test_delete_with_non_existent_user(self, repo, non_existent_user_entity):
        with pytest.raises(UserNotFoundError):
            await repo.delete(non_existent_user_entity.id)
