from unittest.mock import Mock
from src.modules.channels.application.sync_all_data import SyncAllDataService


async def test_update_countries_success():
    mock_task = Mock()
    mock_res = Mock()
    mock_res.id = "test-task-id-123"
    mock_task.delay.return_value = mock_res

    service = SyncAllDataService(mock_task)
    result = await service.execute()

    mock_task.delay.assert_called_once()
    assert result["status"] == "queued"
    assert result["task_id"] == "test-task-id-123"
