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
