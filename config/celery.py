"""
Celery application instance.

Підхоплюється у config/__init__.py щоб app був доступний при імпорті Django.
"""
import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("hr_system")
# Налаштування читаються з settings.py (префікс CELERY_)
app.config_from_object("django.conf:settings", namespace="CELERY")
# Автопошук задач у кожному apps/<x>/tasks.py
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
