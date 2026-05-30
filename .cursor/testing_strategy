# HR Candidate Evaluation System — Testing Strategy

## Philosophy

**Two-layer testing pyramid:**

```
        ┌──────────────┐
        │  Integration │  ~30% — real DB, real HTTP, real JWT
        │    Tests     │
        ├──────────────┤
        │  Unit Tests  │  ~70% — InMemory repos, no DB, instant
        └──────────────┘
```

Unit tests verify business logic in isolation.
Integration tests verify that layers wire together correctly end-to-end.

---

## Directory Structure

```
tests/
├── conftest.py              # Shared fixtures (InMemory repos + DB clients)
├── unit/
│   ├── __init__.py
│   ├── test_enums_transitions.py     # CandidateStatus state machine
│   ├── test_candidate_service.py     # CandidateService full coverage
│   └── test_interview_vacancy.py     # InterviewService + VacancyService
└── integration/
    ├── __init__.py
    ├── test_candidate.py             # /api/v1/candidates/ endpoints
    └── test_vacancy_interview.py     # /api/v1/vacancies/, /interviews/, /analytics/
```

---

## Unit Tests (`tests/unit/`)

### Rules
- **No `@pytest.mark.django_db`** — must not touch the database
- Use `InMemoryXxxRepo` from `conftest.py` instead of Django ORM repos
- Inject repos into services via constructor: `CandidateService(repo=InMemoryCandidateRepo())`
- Use `no_signal` fixture to suppress Django signals when testing status transitions
- Test every branch: happy path, error cases, boundary values, edge cases

### Fixtures (from conftest)
| Fixture | Type | Description |
|---------|------|-------------|
| `candidate_repo` | `InMemoryCandidateRepo` | In-memory candidate store |
| `candidate_service` | `CandidateService` | Service wired to in-memory repo |
| `interview_repo` | `InMemoryInterviewRepo` | In-memory interview store |
| `interview_service` | `InterviewService` | Service wired to in-memory repo |
| `vacancy_repo` | `InMemoryVacancyRepo` | In-memory vacancy store |
| `no_signal` | context | Mocks `candidate_status_changed.send` |

### What to test in unit tests
- All service methods: create, get, list, update, delete, status change
- All valid status transitions
- All forbidden transitions → `ValidationError`
- Idempotent operations (same status twice → no history entry)
- Filtering (by status, search, recruiter_id, etc.)
- Conflict detection (duplicate email → `ConflictError`)
- Boundary values (score 1 OK, score 0 → error, score 10 OK, score 11 → error)
- History recording on transitions

---

## Integration Tests (`tests/integration/`)

### Rules
- Mark with `pytestmark = pytest.mark.django_db` at module level
- Use JWT-authenticated API clients from conftest: `recruiter_client`, `interviewer_client`, `admin_client`, `anon_client`
- Test via HTTP only — do not import service or repo classes
- Use DRF `APIClient` with `format="json"` for all requests

### Fixtures (from conftest)
| Fixture | Role | Description |
|---------|------|-------------|
| `recruiter_user` | RECRUITER | DB user, created fresh per test |
| `interviewer_user` | INTERVIEWER | DB user, created fresh per test |
| `admin_user` | ADMIN | DB user, created fresh per test |
| `recruiter_client` | `APIClient` | JWT-authenticated as recruiter |
| `interviewer_client` | `APIClient` | JWT-authenticated as interviewer |
| `admin_client` | `APIClient` | JWT-authenticated as admin |
| `anon_client` | `APIClient` | Unauthenticated client |

### Mandatory test categories per endpoint

| Category | What to assert |
|----------|----------------|
| **Auth** | `anon_client` → 401; wrong role → 403 |
| **Happy path** | Correct status code, response shape, field values |
| **Validation** | Missing required fields → 400; invalid values → 400 |
| **Not found** | Nonexistent ID → 404 |
| **Conflict** | Duplicate unique constraint → 409 |
| **Role isolation** | Interviewer cannot create/delete; recruiter cannot evaluate |

---

## Running Tests

```bash
# All tests (from project root)
pytest tests/

# Unit only (fast, no DB)
pytest tests/unit/ -v

# Integration only
pytest tests/integration/ -v

# With coverage
pytest tests/ --cov=apps --cov=core --cov-report=term-missing

# Run specific test class
pytest tests/unit/test_candidate_service.py::TestStatusTransitions -v

# Run with markers
pytest -m unit -v
pytest -m integration -v
```

---

## Coverage Targets

| Module | Target |
|--------|--------|
| `apps/candidates/` | ≥ 90% |
| `apps/interviews/` | ≥ 85% |
| `apps/vacancies/` | ≥ 85% |
| `apps/analytics/` | ≥ 80% |
| `core/` | ≥ 90% |

Coverage reports:
- Terminal: `--cov-report=term-missing`
- XML (SonarCloud): `coverage.xml`
- HTML (human): `htmlcov/index.html`

---

## InMemory Repository Contract

All `InMemoryXxxRepo` classes in `conftest.py` implement the same interface as their Django counterparts (`ICandidateRepository` etc.). They must:

1. Start with an empty `_store: dict[int, DTO]`
2. Auto-increment `_next_id` on each `add()`
3. Raise `NotFoundError` (from `core.exceptions`) when item is missing
4. Apply the same filtering logic as the Django repo

If the Django repo adds a new method, the InMemory version must be updated too.

---

## Signal Isolation

Status change tests that call `candidate_service.change_status()` must use the `no_signal` fixture unless explicitly testing signal behavior:

```python
def test_new_to_screening(self, candidate_service, no_signal):
    c = _create(candidate_service)
    updated = candidate_service.change_status(c.id, "SCREENING")
    assert updated.status == "SCREENING"
```

Without `no_signal`, the signal will attempt to fire Celery tasks which fail in the test environment.

---

## Anti-Patterns to Avoid

- ❌ `@pytest.mark.django_db` in unit tests
- ❌ Calling `Model.objects.*` directly in tests (use fixtures or API)
- ❌ `time.sleep()` in tests
- ❌ Tests that depend on ordering or shared mutable state between tests
- ❌ Hardcoded IDs (use fixture return values)
- ❌ Asserting on full response body shape — assert specific fields
- ❌ Duplicating fixtures locally that already exist in `conftest.py`
