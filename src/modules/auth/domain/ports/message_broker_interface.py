from abc import ABC, abstractmethod
from src.modules.auth.domain.value_objects.email import Email


class IMessageBroker(ABC):
    """Interface for message broker."""

    @abstractmethod
    async def send(self, email: Email) -> bool:
        """
        Send a message to message broker.
        """
        pass
