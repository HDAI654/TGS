from src.modules.channels.domain.ports.task_interface import ITask
from workers.tasks import update_all, update_channels, update_countries


def get_sync_all_data_task() -> ITask:
    return update_all


def get_sync_channels_task() -> ITask:
    return update_channels


def get_sync_countries_task() -> ITask:
    return update_countries
