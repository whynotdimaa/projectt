"""
Factory Method для нотифікаційних стратегій.

Сервіс просить фабрику: "дай мені стратегії для каналів [email, slack]" —
і отримує список об'єктів, не знаючи, як вони створюються.

Додавання нового каналу = додати клас + ключ у _REGISTRY. Сервіс не міняється.
"""
from __future__ import annotations

from typing import Iterable

from core.exceptions import ValidationError

from .base import INotificationStrategy
from .email_strategy import EmailStrategy
from .slack_strategy import SlackStrategy
from .sms_strategy import SMSStrategy


_REGISTRY: dict[str, type[INotificationStrategy]] = {
    "email": EmailStrategy,
    "slack": SlackStrategy,
    "sms": SMSStrategy,
}


class NotificationStrategyFactory:
    @staticmethod
    def create(channel: str) -> INotificationStrategy:
        cls = _REGISTRY.get(channel)
        if cls is None:
            raise ValidationError(f"Unknown notification channel: {channel}")
        return cls()

    @staticmethod
    def create_many(channels: Iterable[str]) -> list[INotificationStrategy]:
        return [NotificationStrategyFactory.create(ch) for ch in channels]

    @staticmethod
    def available_channels() -> list[str]:
        return list(_REGISTRY.keys())
