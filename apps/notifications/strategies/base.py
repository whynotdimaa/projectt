"""
Strategy pattern: контракт для каналу нотифікацій.
Додавання нового каналу (Telegram, MS Teams) = новий клас тут,
без змін у NotificationService (Open/Closed Principle).
"""
from abc import ABC, abstractmethod

from ..dto import NotificationMessage


class INotificationStrategy(ABC):
    name: str = "abstract"

    @abstractmethod
    def send(self, message: NotificationMessage) -> None:
        """Надіслати повідомлення. Може кидати винятки — їх ловить Celery retry."""
