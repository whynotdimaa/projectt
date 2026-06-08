# HR Candidate Evaluation System — Cursor Rules

## Project Overview
Django REST Framework backend for an HR Candidate Evaluation System.
Python 3.12, Django 5.x, DRF, PostgreSQL, Redis/Celery, JWT auth.

---

## Code Style & Standards

### Python
- **Python 3.12** with full type annotations on all public functions and methods
- Follow **PEP 8** strictly; max line length = 100 chars
- Use `from __future__ import annotations` in every module
- Prefer `dataclasses` or typed `NamedTuple` for DTOs — never use raw dicts as data contracts
- Use explicit keyword arguments when calling functions with 3+ params

### Naming Conventions
- `snake_case` for variables, functions, modules
- `PascalCase` for classes
- `SCREAMING_SNAKE_CASE` for constants and enums values
- Prefix interfaces with `I`: `ICandidateRepository`, `IInterviewRepository`
- Suffix services with `Service`: `CandidateService`, `VacancyService`
- Suffix repos with `Repository` or `Repo`: `DjangoCandidateRepository`

### Imports Order (isort)
1. Standard library
2. Third-party (`django`, `rest_framework`, `celery`)
3. Internal (`apps.*`, `core.*`)
Separate each group with a blank line.

---

## Architecture Rules

### Layered Clean Architecture (STRICT)
```
Views/Serializers → Services → Repository Interface → Repository Implementation → DB
```
- **Views** handle HTTP only: parse request, call service, return response
- **Services** contain ALL business logic — no ORM calls, no HTTP logic
- **Repositories** abstract all DB access behind interfaces (`apps/*/repositories/interfaces.py`)
- **DTOs** (`apps/*/dto.py`) are the only data contracts between layers
- **NEVER** import Django models into services
- **NEVER** call service methods from serializers

### App Structure (every Django app must follow this)
```
apps/<name>/
  ├── dto.py                  # Input/Output DTOs (dataclasses)
  ├── enums.py                # Django TextChoices enums
  ├── models.py               # Django ORM models only
  ├── signals.py              # Django signals
  ├── admin.py                # Django admin
  ├── apps.py
  ├── repositories/
  │   ├── interfaces.py       # Abstract base class (ICandidateRepository)
  │   └── django_repo.py      # Concrete Django ORM implementation
  ├── services/
  │   └── <name>_service.py   # Business logic, depends on interface
  └── api/
      └── v1/
          ├── serializers.py
          ├── views.py
          └── urls.py
```

### Core Module
```
core/
  ├── exceptions.py    # NotFoundError, ConflictError, ValidationError, etc.
  ├── permissions.py   # DRF permission classes
  └── pagination.py    # DRF pagination
```

---

## Django & DRF Rules

### Models
- Always define `__str__` returning a meaningful string
- Use `verbose_name` and `verbose_name_plural` in Meta
- Migrations must be committed; never edit existing migrations

### Serializers
- Use `read_only_fields` instead of `read_only=True` in field definitions when possible
- Validate business constraints in the service layer, not in serializers
- Serializers are DTOs for HTTP — they should not call services

### Views
- Use `APIView` or `ViewSet` — no `ModelViewSet` shortcuts that bypass the service layer
- Map exceptions to HTTP status codes in the view using try/except:
  - `NotFoundError` → 404
  - `ConflictError` → 409
  - `ValidationError` (core) → 400
- Always set `permission_classes` explicitly on every view

### URLs
- API versioning via URL prefix: `/api/v1/`
- Always use `basename` in `router.register()`
- Router registered in `apps/<name>/api/v1/urls.py`, included in `config/urls.py`

---

## Authentication & Authorization

- JWT via `djangorestframework-simplejwt`
- Roles: `ADMIN`, `RECRUITER`, `INTERVIEWER` (stored in `UserRole` enum)
- Permission classes live in `core/permissions.py`
- Recruiter: full CRUD on candidates, vacancies, interviews
- Interviewer: read-only on candidates/vacancies, evaluate interviews
- Admin: full access

---

## Error Handling

- All domain exceptions extend from `core.exceptions.BaseAppError`
- Exception → HTTP status mapping is done **only in views**
- Never raise `Http404` or `DRF ValidationError` from services
- Log unexpected exceptions with `logger.exception(...)` before re-raising

---

## Testing Rules

- Unit tests: `tests/unit/` — use InMemory repos, NO `@pytest.mark.django_db`
- Integration tests: `tests/integration/` — use real DB, real API client
- Every new service method MUST have unit tests
- Every new API endpoint MUST have integration tests for auth + happy path + error cases
- Use fixtures from `tests/conftest.py` — do not create local fixtures that duplicate globals
- Mark tests with appropriate markers: `@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.api`

---

## Celery & Async

- Tasks defined in `apps/<name>/tasks.py`
- Tasks must be idempotent
- Use `shared_task` decorator
- Never call tasks synchronously in views (use `.delay()` or `.apply_async()`)

---

## Forbidden Patterns

- ❌ Raw SQL queries (use ORM or annotated querysets)
- ❌ Business logic in views or serializers
- ❌ ORM calls in service layer (inject repo via constructor DI)
- ❌ `print()` statements (use `logging`)
- ❌ Hardcoded secrets or URLs (use `django.conf.settings`)
- ❌ `Model.objects.*` calls outside of repository implementations
