from abc import ABC, abstractmethod
from src.modules.auth.domain.value_objects.email import Email


class IEmailSender(ABC):
    """Interface for sending emails."""

    @abstractmethod
    async def send(
        self,
        to: Email,
        subject: str,
        body: str,
        html: str | None = None,
    ) -> None:
        """
        Send an email.

        Raises:
            EmailSendingFailedError: Raised when an email fails to send.
        """
        pass
