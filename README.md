# HR Candidate Evaluation System

Django + DRF застосунок для оцінки кандидатів. Архітектура — **Modular Monolith + Layered Architecture (3-layer) + Repository / Strategy / Observer / Factory** (вище за MVT, нижче за мікросервіси).

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

## Готово ✅

1. ✅ Каркас, модель `Candidate` + enum статусів
2. ✅ Repository + Service для Candidate
3. ✅ DRF API v1 `/api/v1/candidates/`
4. ✅ JWT auth + RBAC (RECRUITER / INTERVIEWER / ADMIN)
5. ✅ Interview, Vacancy, StatusHistory
6. ✅ Strategy + Celery нотифікації (Email / Slack / SMS)
7. ✅ Observer (Django signals) + Analytics (funnel, time-to-hire, by-status)
8. ✅ Tests (pytest), Docker, GitHub Actions CI

## Реалізовані патерни

| Патерн | Де |
|---|---|
| **Repository** | `apps/<domain>/repositories/interfaces.py` + `*_repository.py` |
| **Strategy** | `apps/notifications/strategies/` (Email, Slack, SMS) |
| **Factory Method** | `apps/notifications/strategies/factory.py` (NotificationStrategyFactory) |
| **Observer** | Custom Django Signal `candidate_status_changed` (`apps/candidates/signals.py`) + receiver у `apps/notifications/handlers.py` |
| **Producer-Consumer** | Celery task → Strategy для асинхронних нотифікацій |

## API endpoints

| Метод | URL | Опис |
|---|---|---|
| `POST` | `/api/v1/auth/login/` | JWT login |
| `POST` | `/api/v1/auth/refresh/` | refresh token |
| `GET/POST` | `/api/v1/candidates/` | список / створити |
| `GET/PATCH/DELETE` | `/api/v1/candidates/{id}/` | деталі |
| `PATCH` | `/api/v1/candidates/{id}/status/` | змінити статус (валідація переходу + signal) |
| `GET/POST` | `/api/v1/vacancies/` | вакансії |
| `POST` | `/api/v1/vacancies/{id}/close/` | закрити вакансію |
| `GET/POST` | `/api/v1/interviews/` | інтерв'ю |
| `PATCH` | `/api/v1/interviews/{id}/evaluate/` | оцінити (1-10) |
| `GET` | `/api/v1/analytics/funnel/` | воронка з конверсіями |
| `GET` | `/api/v1/analytics/time-to-hire/` | середній час до hire |
| `GET` | `/api/v1/analytics/candidates-by-status/` | розподіл по статусах |

## Запуск через Docker (повний стек)

```bash
docker compose up --build
```

Підіймаються 4 сервіси: **postgres**, **redis**, **web** (Django), **worker** (Celery).
API: http://localhost:8000/api/v1/

## Запуск локально (без Docker)

```bash
python -m venv .venv
.venv\Scripts\activate            # Windows
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Тести

```bash
pytest tests/ -v
```

## CI

Pipeline `.github/workflows/ci.yml` запускає `manage.py check` + `migrate` + `pytest` із Postgres-сервісом на кожен push/PR.
