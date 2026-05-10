"""Slack-стратегія (заглушка). У production — HTTP виклик у Slack webhook URL."""
import logging

from ..dto import NotificationMessage
from .base import INotificationStrategy

logger = logging.getLogger(__name__)


class SlackStrategy(INotificationStrategy):
    name = "slack"

    def __init__(self, webhook_url: str = "") -> None:
        self._webhook_url = webhook_url

    def send(self, message: NotificationMessage) -> None:
        # TODO production: requests.post(self._webhook_url, json={"text": ...})
        logger.info(
            "[Slack stub] channel=%s subject=%s body=%s",
            message.recipient, message.subject, message.body,
        )
