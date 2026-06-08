"""Тести Strategy + Factory для нотифікацій."""
import pytest

from apps.notifications.dto import NotificationMessage
from apps.notifications.services.notification_service import NotificationService
from apps.notifications.strategies.base import INotificationStrategy
from apps.notifications.strategies.factory import NotificationStrategyFactory
from core.exceptions import ValidationError


def test_factory_creates_known_channels():
    for ch in ("email", "slack", "sms"):
        s = NotificationStrategyFactory.create(ch)
        assert isinstance(s, INotificationStrategy)
        assert s.name == ch


def test_factory_unknown_channel_raises():
    with pytest.raises(ValidationError):
        NotificationStrategyFactory.create("telegram")


def test_factory_create_many():
    items = NotificationStrategyFactory.create_many(["email", "slack"])
    assert len(items) == 2
    assert {s.name for s in items} == {"email", "slack"}


class _SpyStrategy(INotificationStrategy):
    name = "spy"
    def __init__(self): self.calls = []
    def send(self, message): self.calls.append(message)


class _BoomStrategy(INotificationStrategy):
    name = "boom"
    def send(self, message):
        raise RuntimeError("network down")


def test_service_dispatches_to_all_strategies():
    spy1, spy2 = _SpyStrategy(), _SpyStrategy()
    svc = NotificationService(strategies=[spy1, spy2])
    msg = NotificationMessage("a@b.c", "s", "b")
    svc.send(msg)
    assert spy1.calls == [msg]
    assert spy2.calls == [msg]


def test_service_isolates_failing_strategy():
    """Падіння однієї стратегії не блокує інші."""
    spy = _SpyStrategy()
    svc = NotificationService(strategies=[_BoomStrategy(), spy])
    svc.send(NotificationMessage("a@b.c", "s", "b"))
    assert len(spy.calls) == 1


def test_service_for_channels():
    """NotificationService.for_channels() creates strategies via factory."""
    svc = NotificationService.for_channels(["email", "slack"])
    assert len(svc._strategies) == 2
    assert {s.name for s in svc._strategies} == {"email", "slack"}


def test_email_strategy_send():
    """EmailStrategy.send() calls Django send_mail with correct parameters."""
    from unittest.mock import patch
    from apps.notifications.strategies.email_strategy import EmailStrategy
    
    strategy = EmailStrategy(from_email="test@example.com")
    msg = NotificationMessage("recipient@example.com", "Test Subject", "Test Body")
    
    with patch("apps.notifications.strategies.email_strategy.send_mail") as mock_send_mail:
        strategy.send(msg)
        mock_send_mail.assert_called_once_with(
            subject="Test Subject",
            message="Test Body",
            from_email="test@example.com",
            recipient_list=["recipient@example.com"],
            fail_silently=False,
        )


def test_build_status_change_message():
    """build_status_change_message() creates correct NotificationMessage."""
    from apps.notifications.services.notification_service import build_status_change_message
    
    msg = build_status_change_message(
        candidate_email="test@example.com",
        candidate_name="John Doe",
        from_status="NEW",
        to_status="INTERVIEW"
    )
    
    assert msg.recipient == "test@example.com"
    assert msg.subject == "Your application status: INTERVIEW"
    assert "John Doe" in msg.body
    assert "NEW -> INTERVIEW" in msg.body
    assert "HR Team" in msg.body
