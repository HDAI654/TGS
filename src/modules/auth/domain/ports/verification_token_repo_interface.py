from abc import ABC, abstractmethod
from src.modules.auth.domain.value_objects.email import Email
from src.modules.auth.domain.value_objects.email_verification_token import (
    EmailVerificationToken,
)


class IEmailVerificationTokenRepo(ABC):
    """Repository interface for email verification tokens."""

    @abstractmethod
    async def add(
        self,
        token: EmailVerificationToken,
        email: Email,
        token_type: str = "verifyemail",
        ttl_seconds: int = 1440,
    ) -> None:
        """
        Store a verification token for an email.

        Raises:
            CacheConnectionError: Raised when cannot connect to cache.
            CacheTimeoutError: Raised when cache operation times out.
            CacheOperationError: Raised when cache operation fails.
        """
        pass

    @abstractmethod
    async def get(
        self,
        token: EmailVerificationToken,
        token_type: str = "verifyemail",
    ) -> Email | None:
        """
        Retrieve the email associated with a verification token.

        Raises:
            CacheConnectionError: Raised when cannot connect to cache.
            CacheTimeoutError: Raised when cache operation times out.
            CacheOperationError: Raised when cache operation fails.
        """
        pass

    @abstractmethod
    async def delete(
        self,
        token: EmailVerificationToken,
        token_type: str = "verifyemail",
    ) -> None:
        """
        Delete a verification token.

        Raises:
            CacheConnectionError: Raised when cannot connect to cache.
            CacheTimeoutError: Raised when cache operation times out.
            CacheOperationError: Raised when cache operation fails.
        """
        pass
