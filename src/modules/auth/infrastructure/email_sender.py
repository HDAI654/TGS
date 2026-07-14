import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from src.modules.auth.domain.ports.email_sender_interface import IEmailSender
from src.modules.auth.domain.value_objects.email import Email
from src.modules.core.conf import Config
from src.modules.auth.exceptions import EmailSendingFailedError


class ImpEmailSender(IEmailSender):
    async def send(
        self,
        to: Email,
        subject: str,
        body: str,
        html: str | None = None,
    ) -> None:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = Config.FROM_EMAIL
        msg["To"] = to.value

        part_text = MIMEText(body, "plain", "utf-8")
        msg.attach(part_text)

        if html:
            part_html = MIMEText(html, "html", "utf-8")
            msg.attach(part_html)

        try:
            await aiosmtplib.send(
                msg,
                hostname=Config.SMTP_HOST,
                port=Config.SMTP_PORT,
                username=Config.SMTP_USER,
                password=Config.SMTP_PASSWORD,
                use_tls=True,
            )
        except aiosmtplib.SMTPAuthenticationError as e:
            raise EmailSendingFailedError("SMTP authentication failed") from e
        except aiosmtplib.SMTPException as e:
            raise EmailSendingFailedError(f"Failed to send email: {e}") from e
