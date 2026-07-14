from abc import ABC, abstractmethod


class ITask(ABC):
    """An interface for tasks"""

    @abstractmethod
    def delay(self, *args, **kwargs):
        pass
