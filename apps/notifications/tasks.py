"""
Celery-задачі для асинхронної доставки нотифікацій.
Виклик: send_notification_task.delay(channels=[...], message_dict={...})
"""
from __future__ import annotations

import logging

from celery import shared_task
from django.conf import settings

from .dto import NotificationMessage
from .services.notification_service import (
    NotificationService,
    build_status_change_message,
)

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    autoretry_for=(Exception,),  # noqa: BLE001 – intentional: retry on any transient failure
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
    ignore_result=True,
)
def send_notification_task(self, channels: list[str], message_dict: dict) -> None:
    """Загальна задача: стратегії + повідомлення."""
    message = NotificationMessage(**message_dict)
    NotificationService.for_channels(channels).send(message)


@shared_task(ignore_result=True)
def notify_candidate_status_changed(
    candidate_email: str,
    candidate_name: str,
    from_status: str,
    to_status: str,
) -> None:
    """Високорівнева задача-обгортка для зміни статусу кандидата."""
    message = build_status_change_message(
        candidate_email=candidate_email,
        candidate_name=candidate_name,
        from_status=from_status,
        to_status=to_status,
    )
    NotificationService.for_channels(settings.NOTIFICATION_CHANNELS).send(message)
