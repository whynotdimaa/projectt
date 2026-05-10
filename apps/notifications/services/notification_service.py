"""
NotificationService — координатор стратегій.

Не знає про конкретні канали. Усі канали еквівалентні через INotificationStrategy.
Відмова однієї стратегії логується, але не зриває інші (best-effort).
"""
from __future__ import annotations

import logging
from typing import Iterable

from ..dto import NotificationMessage
from ..strategies.base import INotificationStrategy
from ..strategies.factory import NotificationStrategyFactory

logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(self, strategies: list[INotificationStrategy] | None = None) -> None:
        self._strategies = strategies or []

    @classmethod
    def for_channels(cls, channels: Iterable[str]) -> "NotificationService":
        return cls(strategies=NotificationStrategyFactory.create_many(channels))

    def send(self, message: NotificationMessage) -> None:
        for strategy in self._strategies:
            try:
                strategy.send(message)
            except Exception as exc:  # noqa: BLE001
                logger.exception(
                    "Strategy %s failed for recipient=%s: %s",
                    strategy.name, message.recipient, exc,
                )


def build_status_change_message(
    candidate_email: str,
    candidate_name: str,
    from_status: str,
    to_status: str,
) -> NotificationMessage:
    return NotificationMessage(
        recipient=candidate_email,
        subject=f"Your application status: {to_status}",
        body=(
            f"Hi {candidate_name},\n\n"
            f"Your application status changed: {from_status} -> {to_status}.\n\n"
            "HR Team"
        ),
    )
