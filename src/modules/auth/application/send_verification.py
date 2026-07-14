import logging
from datetime import datetime
from src.modules.auth.exceptions import BlockEmail
from src.modules.auth.domain.ports.verification_token_repo_interface import (
    IEmailVerificationTokenRepo,
)
from src.modules.auth.domain.ports.email_sender_interface import IEmailSender
from src.modules.auth.domain.ports.block_email_checker_interface import IEmailChecker
from src.modules.auth.domain.value_objects.email import Email
from src.modules.auth.domain.value_objects.email_verification_token import (
    EmailVerificationToken,
)
from src.modules.core.conf import Config

logger = logging.getLogger(__name__)


class SendVerificationService:
    def __init__(
        self,
        token_repo: IEmailVerificationTokenRepo,
        email_sender: IEmailSender,
        email_checker: IEmailChecker,
    ):
        self.token_repo = token_repo
        self.email_sender = email_sender
        self.email_checker = email_checker

    async def execute(self, email: str) -> None:
        logger.info("Sending email verification")

        email_vo = Email(email)

        # Check email against blocklist
        if await self.email_checker.is_blocked(email_vo):
            raise BlockEmail(f"Email '{email}' is blocked")

        # Create verification token and save it
        ver_token = EmailVerificationToken.generate()
        await self.token_repo.add(
            token=ver_token,
            email=email_vo,
            token_type="verifyemail",
            ttl_seconds=Config.VERIFY_EMAIL_EXPIRE_MINUTES * 60,
        )
        logger.debug("Token added to cache")

        # Send the email
        await self.email_sender.send(
            to=email_vo,
            subject=f"Verify Your Email Address — {Config.APP_NAME}",
            body=self._build_plain_text_body(
                f"{Config.VERIFY_EMAIL_URL}/{ver_token.value}"
            ),
            html=self._build_html_body(f"{Config.VERIFY_EMAIL_URL}/{ver_token.value}"),
        )

        logger.info("Email sent successfully")

    def _build_plain_text_body(self, link: str) -> str:
        return f"""
            Welcome to {Config.APP_NAME}!

            Please verify your email address by clicking the link below:

            {link}

            This link will expire in {Config.VERIFY_EMAIL_EXPIRE_MINUTES // 60} hours.

            If you did not create an account with {Config.APP_NAME}, please ignore this email.

            Need help? Contact us at {Config.SUPPORT_EMAIL}

            — The {Config.APP_NAME} Team
        """.strip()

    def _build_html_body(self, link: str) -> str:
        return f"""
            <!DOCTYPE html>
            <html>
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Verify Your Email</title>
                    <style>
                        body {{
                            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
                            background-color: #f4f4f4;
                            margin: 0;
                            padding: 20px;
                            line-height: 1.6;
                        }}
                        .container {{
                            max-width: 500px;
                            margin: 0 auto;
                            background: #ffffff;
                            padding: 32px 28px;
                            border-radius: 12px;
                            box-shadow: 0 1px 3px rgba(0,0,0,0.06);
                        }}
                        .logo {{
                            text-align: center;
                            font-size: 20px;
                            font-weight: 700;
                            color: #1a1a1a;
                            letter-spacing: -0.5px;
                            margin-bottom: 24px;
                        }}
                        .greeting {{
                            font-size: 16px;
                            color: #1a1a1a;
                            margin: 0 0 8px 0;
                        }}
                        .text {{
                            font-size: 15px;
                            color: #333333;
                            margin: 0 0 18px 0;
                        }}
                        .btn-wrap {{
                            text-align: center;
                            margin: 28px 0 24px 0;
                        }}
                        .btn {{
                            display: inline-block;
                            background-color: #1a1a1a;
                            color: #ffffff;
                            padding: 12px 32px;
                            border-radius: 40px;
                            text-decoration: none;
                            font-weight: 600;
                            font-size: 15px;
                            letter-spacing: 0.3px;
                            border: none;
                        }}
                        .btn:hover {{
                            background-color: #333333;
                        }}
                        .divider {{
                            border: none;
                            border-top: 1px solid #eaeaea;
                            margin: 28px 0 20px 0;
                        }}
                        .footer {{
                            font-size: 12px;
                            color: #888888;
                            text-align: center;
                        }}
                        .footer a {{
                            color: #1a1a1a;
                            text-decoration: underline;
                        }}
                        .link-box {{
                            background: #f7f7f7;
                            padding: 10px 14px;
                            border-radius: 6px;
                            font-size: 13px;
                            word-break: break-all;
                            color: #1a1a1a;
                            margin: 8px 0 18px 0;
                        }}
                        .expiry {{
                            font-size: 13px;
                            color: #666666;
                            margin: 16px 0 0 0;
                        }}
                    </style>
                </head>
                
                <body>
                    <div class="container">
                        <div class="logo">{Config.APP_NAME}</div>

                        <p class="greeting"><strong>Hi there,</strong></p>
                        <p class="text">Thanks for joining {Config.APP_NAME}. Please verify your email address to continue.</p>

                        <div class="btn-wrap">
                            <a href="{link}" class="btn">Verify Email</a>
                        </div>

                        <p class="text" style="font-size: 13px; color: #888888; text-align: center; margin-top: 4px;">
                            Or open this link in your browser:
                        </p>
                        <div class="link-box">{link}</div>

                        <p class="expiry">⏳ This link expires in <strong>{Config.VERIFY_EMAIL_EXPIRE_MINUTES // 60} hours</strong>.</p>

                        <hr class="divider">

                        <div class="footer">
                            <p>If you didn’t request this, you can safely ignore this email.</p>
                            <p>Need help? <a href="mailto:{Config.SUPPORT_EMAIL}">Contact Support</a></p>
                            <p>© {datetime.now().year} {Config.APP_NAME}. All rights reserved.</p>
                        </div>
                    </div>
                </body>
            </html>
        """.strip()
