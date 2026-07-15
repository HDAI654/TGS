from typing import Callable
from functools import wraps
import logging
from strawberry.exceptions import StrawberryGraphQLError
from src.modules.channels.presentation.graphql.v1.error_code import ErrorCodes
from src.modules.channels.exceptions import DomainError, DatabaseError


def error_handler(
    operation: str,
    logger: logging.Logger | None = None,
    custom_errors: dict[type[Exception], tuple[str, str, int]] | None = None,
):
    """
    Decorator to handle GraphQL errors consistently.

    Args:
        operation: Name of the operation (for logging)
        logger: Logger instance
        custom_errors: Dict mapping exceptions to (message, error_code, status)
    """

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)

            except Exception as e:
                if custom_errors:
                    for exc_type, (message, code, status) in custom_errors.items():
                        if isinstance(e, exc_type):
                            raise StrawberryGraphQLError(
                                message=message or str(e),
                                extensions={
                                    "code": code,
                                    "status": status,
                                },
                            )

                if isinstance(e, StrawberryGraphQLError):
                    raise

                if isinstance(e, DomainError):
                    raise StrawberryGraphQLError(
                        message=str(e),
                        extensions={
                            "code": getattr(
                                e, "error_code", ErrorCodes.VALIDATION_ERROR
                            ),
                            "status": 400,
                        },
                    )

                if isinstance(e, DatabaseError):
                    raise StrawberryGraphQLError(
                        message="Database operation failed. Please try again later.",
                        extensions={
                            "code": ErrorCodes.DATABASE_ERROR,
                            "status": 500,
                        },
                    )

                if logger:
                    logger.exception("Unexpected error during %s", operation)

                raise StrawberryGraphQLError(
                    message="Something went wrong. Please try again later.",
                    extensions={
                        "code": ErrorCodes.INTERNAL_ERROR,
                        "status": 500,
                    },
                )

        return wrapper

    return decorator
