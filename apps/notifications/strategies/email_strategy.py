"""Email-стратегія. Зараз — Django console/SMTP backend (керується settings)."""
import logging

from django.core.mail import send_mail

from ..dto import NotificationMessage
from .base import INotificationStrategy

logger = logging.getLogger(__name__)


class EmailStrategy(INotificationStrategy):
    name = "email"

    def __init__(self, from_email: str = "no-reply@hr-system.local") -> None:
        self._from_email = from_email

    def send(self, message: NotificationMessage) -> None:
        send_mail(
            subject=message.subject,
            message=message.body,
            from_email=self._from_email,
            recipient_list=[message.recipient],
            fail_silently=False,
        )
        logger.info("Email sent to %s: %s", message.recipient, message.subject)
