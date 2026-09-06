import os
from uuid import uuid4
import pytest
from httpx import ASGITransport, AsyncClient

pytestmark = pytest.mark.skipif(
    os.getenv("RUN_CHANNELS_E2E") != "1",
    reason="Requires a running PostgreSQL-backed Channels service.",
)


@pytest.mark.asyncio
async def test_health_and_public_graphql():
    from channels_service.presentation.app import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}

        response = await client.post(
            "/graphql",
            json={
                'query': 'query { channels(search: \"   \", limit: 10, offset: 0) { total } }'
            },
        )
        assert response.status_code == 200
        assert response.json()["data"]["channels"] is None
