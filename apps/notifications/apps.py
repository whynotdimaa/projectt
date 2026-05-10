from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.notifications"
    label = "notifications"

    def ready(self) -> None:
        # Імпортуємо handlers — це реєструє @receiver-и для доменних signals.
        from . import handlers  # noqa: F401
