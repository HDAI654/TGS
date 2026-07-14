import pytest
from unittest.mock import AsyncMock, patch
import aiosmtplib
from src.modules.auth.infrastructure.email_sender import ImpEmailSender
from src.modules.auth.domain.value_objects.email import Email
from src.modules.auth.exceptions import EmailSendingFailedError
from src.modules.core.conf import Config


class TestImpEmailSender:
    @pytest.fixture
    def email_sender(self):
        return ImpEmailSender()

    @pytest.fixture
    def email(self):
        return Email("test@example.com")

    async def test_send_email_success(self, email_sender, email):
        with patch("aiosmtplib.send", new_callable=AsyncMock) as mock_send:
            await email_sender.send(
                to=email,
                subject="Test Subject",
                body="Test body",
                html="<p>Test body</p>",
            )

            mock_send.assert_called_once()
            call_args = mock_send.call_args
            msg = call_args[0][0]
            assert msg["Subject"] == "Test Subject"
            assert msg["From"] == Config.FROM_EMAIL
            assert msg["To"] == email.value

    async def test_send_email_without_html(self, email_sender, email):
        with patch("aiosmtplib.send", new_callable=AsyncMock) as mock_send:
            await email_sender.send(
                to=email,
                subject="Test Subject",
                body="Test body",
                html=None,
            )

            mock_send.assert_called_once()

    async def test_send_email_authentication_failed(self, email_sender, email):
        with patch(
            "aiosmtplib.send",
            new_callable=AsyncMock,
            side_effect=aiosmtplib.SMTPAuthenticationError(
                535, b"Authentication failed"
            ),
        ):
            with pytest.raises(EmailSendingFailedError) as exc_info:
                await email_sender.send(
                    to=email,
                    subject="Test",
                    body="Test",
                )

            assert "authentication" in str(exc_info.value)

    async def test_send_email_smtp_exception(self, email_sender, email):
        with patch(
            "aiosmtplib.send",
            new_callable=AsyncMock,
            side_effect=aiosmtplib.SMTPException("SMTP error"),
        ):
            with pytest.raises(EmailSendingFailedError) as exc_info:
                await email_sender.send(
                    to=email,
                    subject="Test",
                    body="Test",
                )

            assert "failed" in str(exc_info.value).lower()
