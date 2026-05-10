"""
Доменні Django signals (Observer pattern).

Сервіс публікує подію `candidate_status_changed` після успішного переходу.
Підписники реєструються незалежно у відповідних apps.AppConfig.ready():
- notifications -> кидає Celery task
- (майбутнє) analytics -> агрегує метрики, audit логер тощо

Подія НЕ містить ORM-моделей — лише примітивні поля. Це робить signal сумісним
з шаром сервісів і безпечним для серіалізації.
"""
from django.dispatch import Signal

# providing_args (док-only): candidate_id, candidate_email, candidate_name,
# from_status, to_status, changed_by_id
candidate_status_changed = Signal()
