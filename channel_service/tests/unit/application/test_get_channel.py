import pytest
from uuid import uuid4
from src.application.queries import get_channel


@pytest.mark.asyncio
async def test_get_channel_found(mock_channel_repo, sample_channel):
    channel_id = sample_channel.id
    mock_channel_repo.get_by_id_return = sample_channel

    result = await get_channel(mock_channel_repo, channel_id)

    assert result == sample_channel
    assert mock_channel_repo.get_by_id_called_with == channel_id


@pytest.mark.asyncio
async def test_get_channel_not_found(mock_channel_repo):
    channel_id = uuid4()
    mock_channel_repo.get_by_id_return = None

    result = await get_channel(mock_channel_repo, channel_id)

    assert result is None
    assert mock_channel_repo.get_by_id_called_with == channel_id


@pytest.mark.asyncio
async def test_get_channel_repository_raises(mock_channel_repo):
    channel_id = uuid4()

    async def raise_exception(*args, **kwargs):
        raise RuntimeError("DB error")

    mock_channel_repo.get_by_id = raise_exception

    with pytest.raises(RuntimeError, match="DB error"):
        await get_channel(mock_channel_repo, channel_id)
