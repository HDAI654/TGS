from abc import ABC, abstractmethod
from src.modules.auth.domain.value_objects.email import Email


class IEmailChecker(ABC):
    """Interface for checking email addresses against blocklists."""

    @abstractmethod
    async def is_blocked(self, email: Email) -> bool:
        """
        Check if an email address is in the blocklist.
        """
        pass
