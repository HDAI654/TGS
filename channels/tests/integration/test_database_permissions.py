import os

import pytest

pytestmark = pytest.mark.skipif(
    os.getenv("RUN_DB_INTEGRATION") != "1",
    reason="Requires the Docker PostgreSQL environment and both database roles.",
)


@pytest.mark.asyncio
async def test_channels_database_role_is_read_only():
    # The production verification is intentionally environment-gated because it
    # requires a PostgreSQL server initialized with the Admin and Channels roles.
    import asyncpg

    database = os.environ["POSTGRES_DB"]
    host = os.environ.get("POSTGRES_HOST", "localhost")
    port = int(os.environ.get("POSTGRES_PORT", "5432"))
    user = os.environ["CHANNELS_DB_USER"]
    password = os.environ["CHANNELS_DB_PASSWORD"]

    connection = await asyncpg.connect(
        user=user, password=password, database=database, host=host, port=port
    )
    try:
        await connection.fetchval("SELECT 1 FROM categories LIMIT 1")
        with pytest.raises(asyncpg.InsufficientPrivilegeError):
            await connection.execute(
                "INSERT INTO categories (name) VALUES ('permission-test')"
            )
    finally:
        await connection.close()
