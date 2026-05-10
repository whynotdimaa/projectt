"""SMS-стратегія (заглушка). У production — Twilio / Nexmo API."""
import logging

from ..dto import NotificationMessage
from .base import INotificationStrategy

logger = logging.getLogger(__name__)


class SMSStrategy(INotificationStrategy):
    name = "sms"

    def send(self, message: NotificationMessage) -> None:
        logger.info(
            "[SMS stub] phone=%s body=%s",
            message.recipient, message.body,
        )
