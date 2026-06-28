import pytest
import logging
from unittest.mock import AsyncMock, MagicMock
from strawberry.exceptions import StrawberryGraphQLError
from src.channel_app.presentation.graphql.v1.error_handler import error_handler
from src.channel_app.presentation.graphql.v1.error_code import ErrorCodes
from src.core.exceptions import DomainError, DatabaseError


# ========== MOCK EXCEPTIONS ==========
class CustomNotFoundError(Exception):
    pass


class CustomDuplicateError(Exception):
    pass


class CustomPermissionError(Exception):
    pass


class SpecificDomainError(DomainError):
    def __init__(self, message: str):
        self.error_code = "SPECIFIC_ERROR"
        super().__init__(message)


# ========== TESTS ==========
class TestErrorHandler:

    @pytest.fixture
    def async_func(self):
        """Create an async function that can be decorated."""
        return AsyncMock()

    # ========== SUCCESS CASES ==========
    async def test_successful_execution(self, async_func):
        """Test that successful execution returns the result."""

        @error_handler("test_operation")
        async def decorated_func(*args, **kwargs):
            return await async_func(*args, **kwargs)

        expected = {"id": 1, "name": "Test"}
        async_func.return_value = expected

        result = await decorated_func()

        assert result == expected
        async_func.assert_called_once()

    # ========== DOMAIN ERROR CASES ==========
    async def test_domain_error_handling(self, async_func):
        """Test that DomainError is converted to GraphQL error."""

        @error_handler("test_operation")
        async def decorated_func(*args, **kwargs):
            return await async_func(*args, **kwargs)

        domain_error = DomainError("Invalid input: email is required")
        async_func.side_effect = domain_error

        with pytest.raises(StrawberryGraphQLError) as exc_info:
            await decorated_func()

        error = exc_info.value
        assert str(error) == "Invalid input: email is required"
        assert error.extensions["code"] == ErrorCodes.VALIDATION_ERROR
        assert error.extensions["status"] == 400

    async def test_domain_error_with_custom_code(self, async_func):
        """Test DomainError with custom error_code attribute."""

        @error_handler("test_operation")
        async def decorated_func(*args, **kwargs):
            return await async_func(*args, **kwargs)

        domain_error = SpecificDomainError("Specific error occurred")
        async_func.side_effect = domain_error

        with pytest.raises(StrawberryGraphQLError) as exc_info:
            await decorated_func()

        error = exc_info.value
        assert error.extensions["code"] == "SPECIFIC_ERROR"

    # ========== DATABASE ERROR CASES ==========
    async def test_database_error_handling(self, async_func):
        """Test that DatabaseError is converted to GraphQL error with logging."""

        @error_handler("test_operation")
        async def decorated_func(*args, **kwargs):
            return await async_func(*args, **kwargs)

        db_error = DatabaseError("Connection timeout")
        async_func.side_effect = db_error

        with pytest.raises(StrawberryGraphQLError) as exc_info:
            await decorated_func()

        error = exc_info.value
        assert str(error) == "Database operation failed. Please try again later."
        assert error.extensions["code"] == ErrorCodes.DATABASE_ERROR
        assert error.extensions["status"] == 500

    # ========== CUSTOM ERROR CASES ==========
    async def test_custom_error_handling(self, async_func):
        """Test custom error mapping."""

        @error_handler(
            "test_operation",
            custom_errors={
                CustomNotFoundError: ("Resource not found", "NOT_FOUND", 404),
                CustomDuplicateError: ("Resource already exists", "DUPLICATE", 409),
            },
        )
        async def decorated_func(*args, **kwargs):
            return await async_func(*args, **kwargs)

        async_func.side_effect = CustomNotFoundError("Custom not found")

        with pytest.raises(StrawberryGraphQLError) as exc_info:
            await decorated_func()

        error = exc_info.value
        assert str(error) == "Resource not found"
        assert error.extensions["code"] == "NOT_FOUND"
        assert error.extensions["status"] == 404

    async def test_custom_error_without_custom_errors(self, async_func):
        """Test custom_errors=None (no custom mapping)."""

        @error_handler("test_operation", custom_errors=None)
        async def decorated_func(*args, **kwargs):
            return await async_func(*args, **kwargs)

        async_func.side_effect = ValueError("Some error")

        with pytest.raises(StrawberryGraphQLError) as exc_info:
            await decorated_func()

        error = exc_info.value
        assert error.extensions["code"] == ErrorCodes.INTERNAL_ERROR
        assert error.extensions["status"] == 500

    # ========== UNEXPECTED ERROR CASES ==========
    async def test_unexpected_error_handling(self, async_func):
        """Test that unexpected errors are caught and logged."""

        @error_handler("test_operation")
        async def decorated_func(*args, **kwargs):
            return await async_func(*args, **kwargs)

        async_func.side_effect = ValueError("Unexpected value error")

        with pytest.raises(StrawberryGraphQLError) as exc_info:
            await decorated_func()

        error = exc_info.value
        assert str(error) == "Something went wrong. Please try again later."
        assert error.extensions["code"] == ErrorCodes.INTERNAL_ERROR
        assert error.extensions["status"] == 500

    async def test_strawberry_error_passthrough(self, async_func):
        """Test that StrawberryGraphQLError is re-raised as-is."""

        @error_handler("test_operation")
        async def decorated_func(*args, **kwargs):
            return await async_func(*args, **kwargs)

        original_error = StrawberryGraphQLError(
            "Already handled error",
            extensions={"code": "ALREADY_HANDLED", "status": 400},
        )
        async_func.side_effect = original_error

        with pytest.raises(StrawberryGraphQLError) as exc_info:
            await decorated_func()

        error = exc_info.value
        assert error is original_error
        assert error.extensions["code"] == "ALREADY_HANDLED"

    # ========== INTEGRATION TEST ==========
    async def test_full_integration_with_custom_errors(self, async_func):
        """Test full integration with custom errors and logging."""

        @error_handler(
            "add_member",
            custom_errors={
                CustomNotFoundError: ("Member not found", "MEMBER_NOT_FOUND", 404),
                CustomDuplicateError: (
                    "Member already exists",
                    "DUPLICATE_MEMBER",
                    409,
                ),
                CustomPermissionError: ("Permission denied", "FORBIDDEN", 403),
            },
        )
        async def decorated_func(*args, **kwargs):
            return await async_func(*args, **kwargs)

        # Test each custom error
        for error_class, expected_message, expected_code, expected_status in [
            (CustomNotFoundError, "Member not found", "MEMBER_NOT_FOUND", 404),
            (CustomDuplicateError, "Member already exists", "DUPLICATE_MEMBER", 409),
            (CustomPermissionError, "Permission denied", "FORBIDDEN", 403),
        ]:
            async_func.side_effect = error_class("Some error")

            with pytest.raises(StrawberryGraphQLError) as exc_info:
                await decorated_func()

            error = exc_info.value
            assert str(error) == expected_message
            assert error.extensions["code"] == expected_code
            assert error.extensions["status"] == expected_status
