from unittest.mock import MagicMock, patch
from src.channel_app.application.sync_all_data import SyncAllDataService


async def test_update_countries_success():
    mock_task = MagicMock()
    mock_task.id = "test-task-id-123"

    with patch(
        "src.channel_app.application.sync_all_data.update_all"
    ) as mock_update_countries:
        mock_update_countries.delay.return_value = mock_task

        service = SyncAllDataService()
        result = await service.execute()

        mock_update_countries.delay.assert_called_once()
        assert result["status"] == "queued"
        assert result["task_id"] == "test-task-id-123"
