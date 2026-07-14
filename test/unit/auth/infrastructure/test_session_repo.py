import pytest
import fakeredis.aioredis
from uuid import uuid4
from src.modules.auth.domain.entities.session import SessionEntity
from src.modules.auth.domain.entities.session import SessionEntity
from src.modules.auth.domain.value_objects.device import Device
from src.modules.auth.domain.value_objects.date import Date
from src.modules.auth.domain.value_objects.user_id import UserID
from src.modules.auth.domain.value_objects.session_id import SessionID
from src.modules.auth.exceptions import SessionNotFoundError
from src.modules.auth.domain.ports.session_repo_interface import ISessionRepository
from src.modules.auth.infrastructure.cache.redis_session_repo import (
    RedisSessionRepository,
)
from src.modules.core.conf import Config


class TestSessionRepo:
    SESSION_TTL_SECONDS = Config.REFRESH_TOKEN_EXPIRE_MINUTES * 60

    @pytest.fixture
    async def redis_client(self):
        client = fakeredis.aioredis.FakeRedis(decode_responses=True)
        yield client
        await client.flushall()
        await client.aclose()

    @pytest.fixture
    async def session_repo(self, redis_client) -> ISessionRepository:
        return RedisSessionRepository(redis_client)

    @pytest.fixture
    async def serialized_session(self):
        return {
            "id": str(uuid4()),
            "user_id": str(uuid4()),
            "device": "IOS",
            "created_at": "2026-05-21",
        }

    @pytest.fixture
    async def session_entity(self, serialized_session):
        return SessionEntity(
            id=SessionID(serialized_session["id"]),
            user_id=UserID(serialized_session["user_id"]),
            device=Device(serialized_session["device"]),
            created_at=Date(serialized_session["created_at"]),
        )

    @pytest.fixture
    async def session_seed(
        self, session_repo, redis_client, session_entity, serialized_session
    ):
        pipeline = redis_client.pipeline()

        session_key = f"{session_repo.SESSION_KEY_PREFIX}{session_entity.id.value}"
        session_data = serialized_session

        pipeline.hset(session_key, mapping=session_data)
        pipeline.expire(session_key, session_repo.SESSION_TTL_SECONDS)

        user_sessions_key = (
            f"{session_repo.USER_SESSIONS_KEY_PREFIX}{session_entity.user_id.value}"
        )
        pipeline.sadd(user_sessions_key, str(session_entity.id.value))

        await pipeline.execute()

    @pytest.fixture
    async def session_key(self, session_entity, session_repo):
        return f"{session_repo.SESSION_KEY_PREFIX}{session_entity.id.value}"

    @pytest.fixture
    async def user_sessions_key(self, session_entity, session_repo):
        return f"{session_repo.USER_SESSIONS_KEY_PREFIX}{session_entity.user_id.value}"

    async def test_add_session(
        self, session_repo, session_entity, redis_client, session_key, user_sessions_key
    ):
        await session_repo.add(session_entity)

        data = await redis_client.hgetall(session_key)
        assert data is not None
        assert data["user_id"] == session_entity.user_id.value
        assert data["device"] == session_entity.device.value
        assert data["created_at"] == session_entity.created_at.value.isoformat()

        session_ids = await redis_client.smembers(user_sessions_key)
        print(session_ids)

        assert session_entity.id.value in session_ids

    async def test_extend_session_successfully(
        self, session_repo, session_entity, redis_client, session_seed, session_key
    ):
        await session_repo.extend_session(session_entity.id)

        ttl = await redis_client.ttl(session_key)
        assert ttl == session_repo.SESSION_TTL_SECONDS

    async def test_extend_session_with_non_existent_session(
        self, session_repo, redis_client
    ):
        id = SessionID.generate()
        with pytest.raises(SessionNotFoundError):
            await session_repo.extend_session(id)

    async def test_delete_session_successfully(
        self,
        session_repo,
        redis_client,
        session_seed,
        session_entity,
        session_key,
        user_sessions_key,
    ):
        await session_repo.delete(
            session_id=session_entity.id, user_id=session_entity.user_id
        )

        session_data = await redis_client.hgetall(session_key)

        assert not session_data

        session_ids = await redis_client.smembers(user_sessions_key)
        assert session_entity.id.value not in session_ids

    async def test_delete_session_with_non_existent_session(
        self, session_repo, session_seed
    ):
        with pytest.raises(SessionNotFoundError):
            await session_repo.delete(
                session_id=SessionID.generate(), user_id=UserID.generate()
            )

    async def test_delete_all_other_sessions_successfully(
        self, session_repo, redis_client, session_seed, session_entity
    ):
        # create two new sessions for this user
        pipeline = redis_client.pipeline()
        session1 = SessionEntity(
            id=SessionID.generate(),
            user_id=session_entity.user_id,
            device=Device("Android"),
            created_at=Date("2026-07-09"),
        )
        session2 = SessionEntity(
            id=SessionID.generate(),
            user_id=session1.user_id,
            device=Device("IOS"),
            created_at=Date("2026-07-09"),
        )
        session1_key = f"{session_repo.SESSION_KEY_PREFIX}{session1.id.value}"
        session1_data = {
            "id": session1.id.value,
            "user_id": session1.user_id.value,
            "device": session1.device.value,
            "created_at": session1.created_at.value.isoformat(),
        }
        session2_key = f"{session_repo.SESSION_KEY_PREFIX}{session2.id.value}"
        session2_data = {
            "id": session2.id.value,
            "user_id": session2.user_id.value,
            "device": session2.device.value,
            "created_at": session2.created_at.value.isoformat(),
        }

        pipeline.hset(session1_key, mapping=session1_data)
        pipeline.expire(session1_key, session_repo.SESSION_TTL_SECONDS)
        pipeline.hset(session2_key, mapping=session2_data)
        pipeline.expire(session2_key, session_repo.SESSION_TTL_SECONDS)

        user_sessions_key = (
            f"{session_repo.USER_SESSIONS_KEY_PREFIX}{session1.user_id.value}"
        )
        pipeline.sadd(user_sessions_key, str(session1.id.value))
        pipeline.sadd(user_sessions_key, str(session2.id.value))

        await pipeline.execute()

        await session_repo.delete_all_other_sessions(
            current_session_id=session_entity.id, user_id=session_entity.user_id
        )

        res1 = await redis_client.hgetall(session1_key)
        assert not res1

        res2 = await redis_client.hgetall(session2_key)
        assert not res2

        session_ids = await redis_client.smembers(user_sessions_key)
        assert (
            session1.id.value not in session_ids
            and session2.id.value not in session_ids
        )

    async def test_get_by_id_successfully(
        self, session_repo, session_seed, session_entity
    ):
        session = await session_repo.get_by_id(session_id=session_entity.id)

        assert session.id == session_entity.id
        assert session.user_id == session_entity.user_id
        assert session.device == session_entity.device
        assert session.created_at == session_entity.created_at

    async def test_get_by_user_id_successfully(
        self,
        session_repo,
        redis_client,
        session_seed,
        session_entity,
        user_sessions_key,
    ):
        pipeline = redis_client.pipeline()
        session1 = SessionEntity(
            id=SessionID.generate(),
            user_id=session_entity.user_id,
            device=Device("Android"),
            created_at=Date("2026-07-09"),
        )
        session1_key = f"{session_repo.SESSION_KEY_PREFIX}{session1.id.value}"
        session1_data = {
            "id": session1.id.value,
            "user_id": session1.user_id.value,
            "device": session1.device.value,
            "created_at": session1.created_at.value.isoformat(),
        }

        pipeline.hset(session1_key, mapping=session1_data)
        pipeline.expire(session1_key, session_repo.SESSION_TTL_SECONDS)

        pipeline.sadd(user_sessions_key, str(session1.id.value))

        await pipeline.execute()

        sessions = await session_repo.get_by_user_id(user_id=session_entity.user_id)

        sessions_id = {s.id.value for s in sessions if isinstance(s, SessionEntity)}
        assert len(sessions_id) == 2

    async def test_cleanup(
        self,
        session_repo,
        redis_client,
        session_seed,
        session_entity,
        user_sessions_key,
    ):

        # create session but not add it and just add it to user's session list
        pipeline = redis_client.pipeline()
        session1 = SessionEntity(
            id=SessionID.generate(),
            user_id=session_entity.user_id,
            device=Device("Android"),
            created_at=Date("2026-07-09"),
        )
        pipeline.sadd(user_sessions_key, str(session1.id.value))

        await pipeline.execute()

        sessions = await session_repo.get_by_user_id(user_id=session_entity.user_id)

        sessions_id = {s.id.value for s in sessions if isinstance(s, SessionEntity)}
        assert len(sessions_id) == 1
