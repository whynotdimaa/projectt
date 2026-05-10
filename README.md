# HR Candidate Evaluation System

Django + DRF застосунок для оцінки кандидатів. Архітектура — **Modular Monolith + Layered Architecture (3-layer) + Repository Pattern** (вище за MVT, нижче за мікросервіси).

## Шари (одностороння залежність)

```
api (DRF views)  →  services (бізнес-логіка)  →  repositories  →  models (ORM)
```

- **api/** — HTTP, серіалізація, валідація. НЕ ходить в ORM.
- **services/** — бізнес-правила, переходи статусів, події. Не знає про HTTP.
- **repositories/** — єдина точка доступу до даних. Реалізує інтерфейс із `core/repositories/base.py`.
- **models/** — Django ORM, лише схема + інваріанти БД.

## Модулі (apps)

Кожен `apps/<domain>/` — самодостатній модуль із власними `models / repositories / services / api`. Готово до майбутнього виділення в окремий сервіс.

- `apps/candidates/` — ✅ Крок 1 (модель + enum)
- `apps/users/` — Крок 4
- `apps/interviews/`, `apps/vacancies/` — Крок 5
- `apps/analytics/` — Крок 7

## Швидкий старт (локально, SQLite)

```bash
python -m venv .venv
.venv\Scripts\activate            # Windows
pip install -r requirements.txt
copy .env.example .env            # Windows
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Адмінка: http://127.0.0.1:8000/admin/

## Roadmap

1. ✅ Каркас, модель `Candidate` + enum статусів
2. Repository + Service для Candidate (переходи статусів)
3. DRF API v1 `/api/v1/candidates/`
4. JWT auth + RBAC (RECRUITER / INTERVIEWER / ADMIN)
5. Interview, Vacancy, StatusHistory
6. Strategy + Celery нотифікації (Email / Slack / SMS)
7. Observer (signals) + Analytics (funnel, time-to-hire)
8. Tests (pytest), Docker, GitHub Actions CI

## Патерни (заплановані)

| Патерн | Де | Крок |
|---|---|---|
| Repository | `core/repositories/base.py` + `apps/*/repositories/` | 2 |
| Strategy | `apps/notifications/strategies/` | 6 |
| Observer | Django signals → Celery | 7 |
| Factory Method | `apps/analytics/reports/factory.py` | 7 |
| Singleton | Django вже керує connection pool | — |
