from unittest.mock import MagicMock, patch
from src.channel_app.application.sync_countries_data import SyncCountriesService


async def test_update_countries_success():
    mock_task = MagicMock()
    mock_task.id = "test-task-id-123"

    with patch(
        "src.channel_app.application.sync_countries_data.update_countries"
    ) as mock_update_countries:
        mock_update_countries.delay.return_value = mock_task

        service = SyncCountriesService()
        result = await service.execute()

        mock_update_countries.delay.assert_called_once()
        assert result["status"] == "queued"
        assert result["task_id"] == "test-task-id-123"
