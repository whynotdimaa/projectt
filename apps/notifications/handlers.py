"""
Слухачі доменних signals.
Реєструються у apps.NotificationsConfig.ready().
"""
import logging

from django.dispatch import receiver

from apps.candidates.signals import candidate_status_changed

from .tasks import notify_candidate_status_changed

logger = logging.getLogger(__name__)


@receiver(candidate_status_changed)
def on_candidate_status_changed(
    sender,
    candidate_email: str,
    candidate_name: str,
    from_status: str,
    to_status: str,
    **_,
):
    logger.info(
        "Observer[notifications]: dispatching async notification for %s (%s->%s)",
        candidate_email, from_status, to_status,
    )
    notify_candidate_status_changed.delay(
        candidate_email=candidate_email,
        candidate_name=candidate_name,
        from_status=from_status,
        to_status=to_status,
    )
