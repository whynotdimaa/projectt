"""DTO для нотифікацій. Чистий dataclass, серіалізується у JSON для Celery."""
from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class NotificationMessage:
    recipient: str         # email / slack channel / phone
    subject: str
    body: str

    def to_dict(self) -> dict:
        return asdict(self)
