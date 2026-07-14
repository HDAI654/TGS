# TODO: make blocklist dynamic + a static one
from src.modules.auth.domain.ports.block_email_checker_interface import IEmailChecker
from src.modules.auth.domain.value_objects.email import Email

BLOCKLIST = {
    "mailinator.com",
    "temp-mail.org",
    "guerrillamail.com",
    "10minutemail.com",
    "yopmail.com",
    "trashmail.com",
    "throwawaymail.com",
    "emailondeck.com",
    "mail.tm",
    "tempmail.net",
}


class ImpEmailChecker(IEmailChecker):
    async def is_blocked(self, email: Email) -> bool:
        domain = email.value.split("@")[1]
        return domain in BLOCKLIST
