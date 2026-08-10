import asyncio
import smtplib
from email.message import EmailMessage

from src.app.ports import EmailSender
from src.entities.exceptions import InkFigError
from src.infrastructure.config import settings


class EmailDeliveryNotConfiguredError(InkFigError):
    code = "email_delivery_not_configured"


class SmtpEmailSender(EmailSender):
    async def send_signup_verification_code(self, email: str, code: str) -> None:
        if settings.smtp_host is None or settings.smtp_from_email is None:
            raise EmailDeliveryNotConfiguredError("SMTP email delivery is not configured.")
        smtp_host = settings.smtp_host

        message = EmailMessage()
        message["Subject"] = "InkFig signup verification code"
        message["From"] = settings.smtp_from_email
        message["To"] = email
        message.set_content(
            "Your InkFig signup verification code is:\n\n"
            f"{code}\n\n"
            "This code expires soon. If you did not request it, ignore this email."
        )

        await asyncio.to_thread(self._send_message, smtp_host, message)

    def _send_message(self, smtp_host: str, message: EmailMessage) -> None:
        with smtplib.SMTP(smtp_host, settings.smtp_port, timeout=20) as smtp:
            if settings.smtp_use_tls:
                smtp.starttls()
            if settings.smtp_username is not None and settings.smtp_password is not None:
                smtp.login(settings.smtp_username, settings.smtp_password)
            smtp.send_message(message)
