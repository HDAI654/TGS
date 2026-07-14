from abc import ABC, abstractmethod


class ITask(ABC):
    """Interface for workers' tasks"""

    @abstractmethod
    def delay(self, *args, **kwargs) -> None:
        pass
