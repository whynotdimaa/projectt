# HR Candidate Evaluation System

[![CI Pipeline](https://github.com/whynotdimaa/projectt/actions/workflows/ci.yml/badge.svg)](https://github.com/whynotdimaa/projectt/actions/workflows/ci.yml)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=whynotdimaa_projectt&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=whynotdimaa_projectt)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=whynotdimaa_projectt&metric=coverage)](https://sonarcloud.io/summary/new_code?id=whynotdimaa_projectt)
[![Bugs](https://sonarcloud.io/api/project_badges/measure?project=whynotdimaa_projectt&metric=bugs)](https://sonarcloud.io/summary/new_code?id=whynotdimaa_projectt)
[![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=whynotdimaa_projectt&metric=code_smells)](https://sonarcloud.io/summary/new_code?id=whynotdimaa_projectt)
[![Vulnerabilities](https://sonarcloud.io/api/project_badges/measure?project=whynotdimaa_projectt&metric=vulnerabilities)](https://sonarcloud.io/summary/new_code?id=whynotdimaa_projectt)

Django + DRF система управління HR-воронкою кандидатів із повноцінним CI/CD, 100% покриттям коду та інтеграцією SonarCloud.

---

## 🏗️ Архітектура

**Modular Monolith** із чітким розділенням на шари (Clean Architecture):

```
HTTP Request
    ↓
[DRF Views / Serializers]   ← HTTP layer, no business logic
    ↓  DTOs
[Services]                  ← Business logic, domain rules
    ↓  Repository Interface (DIP)
[Repository Implementation] ← Django ORM abstraction
    ↓
[PostgreSQL]
```

### Шари
| Шар | Відповідальність |
|-----|-----------------|
| `api/v1/views.py` | HTTP, серіалізація, маршрутизація |
| `services/` | Бізнес-логіка, переходи статусів, валідація |
| `repositories/interfaces.py` | Абстрактний контракт (DIP) |
| `repositories/*_repository.py` | Django ORM реалізація |
| `models.py` | Django ORM, лише схема БД |

---

## 🔄 Воронка статусів кандидата

```
NEW ──→ SCREENING ──→ INTERVIEW ──→ OFFER ──→ HIRED (terminal)
 │           │              │          │
 └───────────┴──────────────┴──────────┴──→ REJECTED (terminal)
```

Переходи суворо обмежені `ALLOWED_TRANSITIONS` в `apps/candidates/enums.py`. Кожен перехід логується в `StatusHistory`.

---

## 🧩 Реалізовані GoF Патерни

| Патерн | Де | Опис |
|--------|----|------|
| **Repository** | `apps/*/repositories/` | Абстракція доступу до даних, DI через інтерфейси |
| **Strategy** | `apps/notifications/strategies/` | Email, Slack, SMS — взаємозамінні стратегії доставки |
| **Factory Method** | `apps/notifications/strategies/factory.py` | `NotificationStrategyFactory.create(channel)` |
| **Observer** | `apps/candidates/signals.py` + `apps/notifications/handlers.py` | Django Signal при зміні статусу |
| **Producer-Consumer** | `apps/notifications/tasks.py` | Celery task → асинхронна нотифікація |

---

## 📊 Метрики якості

| Метрика | Значення |
|---------|---------|
| **Покриття коду** | ~100% (мін. вимога: 70%) |
| **Кількість тестів** | 200+ (unit + integration) |
| **Bugs** | 0 |
| **Vulnerabilities** | 0 |
| **Code Smells** | A |

---

## 📁 Структура репозиторію

```
project/
├── apps/
│   ├── candidates/          # Кандидати, статуси, воронка
│   │   ├── dto.py
│   │   ├── enums.py         # CandidateStatus + ALLOWED_TRANSITIONS
│   │   ├── models.py
│   │   ├── repositories/    # ICandidateRepository + Django impl
│   │   ├── services/        # CandidateService (бізнес-логіка)
│   │   └── api/v1/
│   ├── interviews/          # Планування та оцінка інтерв'ю
│   ├── vacancies/           # Вакансії
│   ├── analytics/           # Funnel, time-to-hire, by-status
│   ├── notifications/       # Strategy + Celery tasks
│   └── users/               # JWT auth, RBAC ролі
├── core/
│   ├── exceptions.py        # NotFoundError, ConflictError, ValidationError
│   ├── permissions.py       # DRF permission classes
│   └── drf_exception_handler.py
├── tests/
│   ├── conftest.py          # InMemory repos + JWT clients
│   ├── unit/                # ~100 unit tests (no DB)
│   └── integration/         # ~100 integration tests (real DB + API)
├── docs/
│   └── diagrams/            # UML діаграми
├── .cursor/
│   ├── rules                # Coding standards & forbidden patterns
│   ├── architecture         # System architecture description
│   └── testing_strategy     # Testing pyramid & coverage targets
├── .cursorrules             # AI agent global rules
├── .github/workflows/ci.yml # CI/CD pipeline
├── sonar-project.properties # SonarCloud config
├── pytest.ini               # Test runner + coverage config
├── .coveragerc              # Coverage exclusions
├── Dockerfile
└── docker-compose.yml
```

---

## 🚀 Швидкий старт

### Локально (SQLite)
```bash
python -m venv .venv
.venv\Scripts\activate            # Windows
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py runserver
```

### Docker (повний стек: Postgres + Redis + Celery)
```bash
docker compose up --build
```

API: http://localhost:8000/api/v1/  
Swagger: http://localhost:8000/api/schema/swagger-ui/  
Admin: http://localhost:8000/admin/

---

## 🔌 API Endpoints

| Метод | URL | Роль | Опис |
|-------|-----|------|------|
| `POST` | `/api/v1/auth/register/` | Any | Реєстрація |
| `POST` | `/api/v1/auth/login/` | Any | JWT login |
| `POST` | `/api/v1/auth/refresh/` | Any | Refresh token |
| `GET/POST` | `/api/v1/candidates/` | R/I | Список / створити |
| `GET/PATCH/DELETE` | `/api/v1/candidates/{id}/` | R/I | Деталі кандидата |
| `PATCH` | `/api/v1/candidates/{id}/status/` | R | Змінити статус (state machine) |
| `GET/POST` | `/api/v1/vacancies/` | R/I | Вакансії |
| `POST` | `/api/v1/vacancies/{id}/close/` | R | Закрити вакансію |
| `GET/POST` | `/api/v1/interviews/` | R/I | Інтерв'ю |
| `PATCH` | `/api/v1/interviews/{id}/evaluate/` | I | Оцінити (1-10) |
| `GET` | `/api/v1/analytics/funnel/` | R/I | Воронка конверсій |
| `GET` | `/api/v1/analytics/time-to-hire/` | R/I | Середній час найму |
| `GET` | `/api/v1/analytics/candidates-by-status/` | R/I | Розподіл по статусах |

**R** = Recruiter/Admin, **I** = Interviewer (read-only)

---

## 🧪 Тестування

```bash
# Всі тести з покриттям
pytest

# Тільки unit (без DB, швидко)
pytest tests/unit/ --no-cov -q

# Тільки інтеграційні
pytest tests/integration/ --no-cov -q
```

Звіти після запуску:
- `htmlcov/index.html` — HTML покриття (відкрити в браузері)
- `coverage.xml` — для SonarCloud
- `junit.xml` — тестові результати

---

## ⚙️ CI/CD Pipeline

`.github/workflows/ci.yml` при кожному push/PR:

1. 🐘 Запускає Postgres 16 + Redis 7
2. ✅ `python manage.py check` — системна перевірка
3. 🔄 `python manage.py migrate`
4. 🧪 `pytest` — 200+ тестів + coverage
5. 📊 SonarCloud scan
6. 💬 Coverage comment на PR
7. 📦 Upload артефактів: `htmlcov/`, `coverage.xml`, `junit.xml`

---

## 🛡️ Branch Protection

- PR не можна merge якщо CI "червоний"
- Quality Gate SonarCloud повинен бути "passed"
- Coverage < 70% → автоматичне блокування

---

## 📐 UML Діаграми

Дивись [`docs/diagrams/`](docs/diagrams/):
- [Use Case Diagram](docs/diagrams/use_case.md)
- [Domain Model](docs/diagrams/domain_model.md)
- [Class Diagram](docs/diagrams/class_diagram.md)
