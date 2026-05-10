"""
Unit-тести CandidateService із in-memory mock-репозиторієм.
Демонструє користь Repository pattern: сервіс перевіряється БЕЗ БД.
"""
from datetime import datetime, timezone
from typing import Iterable, Optional
from unittest.mock import patch

import pytest

from apps.candidates.dto import (
    CandidateCreateDTO,
    CandidateDTO,
    CandidateFilterDTO,
    CandidateUpdateDTO,
)
from apps.candidates.repositories.interfaces import ICandidateRepository
from apps.candidates.services.candidate_service import CandidateService
from core.exceptions import ConflictError, NotFoundError, ValidationError


class InMemoryCandidateRepo(ICandidateRepository):
    def __init__(self) -> None:
        self._store: dict[int, CandidateDTO] = {}
        self._history: list[dict] = []
        self._next_id = 1

    def get_by_id(self, candidate_id: int) -> Optional[CandidateDTO]:
        return self._store.get(candidate_id)

    def get_by_email(self, email: str) -> Optional[CandidateDTO]:
        for c in self._store.values():
            if c.email.lower() == email.lower():
                return c
        return None

    def list(self, filters: CandidateFilterDTO) -> Iterable[CandidateDTO]:
        items = list(self._store.values())
        if filters.status:
            items = [c for c in items if c.status == filters.status]
        return items

    def add(self, data: CandidateCreateDTO) -> CandidateDTO:
        now = datetime.now(timezone.utc)
        dto = CandidateDTO(
            id=self._next_id,
            first_name=data.first_name, last_name=data.last_name,
            email=data.email, phone=data.phone, resume_url=data.resume_url,
            desired_position=data.desired_position, status="NEW",
            created_at=now, updated_at=now,
        )
        self._store[self._next_id] = dto
        self._next_id += 1
        return dto

    def update(self, candidate_id: int, data: CandidateUpdateDTO) -> CandidateDTO:
        c = self._store.get(candidate_id)
        if not c:
            raise NotFoundError(f"Candidate {candidate_id} not found")
        return c

    def update_status(self, candidate_id: int, new_status: str) -> CandidateDTO:
        c = self._store[candidate_id]
        updated = CandidateDTO(**{**c.__dict__, "status": new_status})
        self._store[candidate_id] = updated
        return updated

    def add_status_history(self, candidate_id, from_status, to_status, changed_by_id) -> None:
        self._history.append({
            "candidate_id": candidate_id,
            "from_status": from_status, "to_status": to_status,
            "changed_by_id": changed_by_id,
        })

    def delete(self, candidate_id: int) -> None:
        if candidate_id not in self._store:
            raise NotFoundError(f"Candidate {candidate_id} not found")
        del self._store[candidate_id]


@pytest.fixture
def service():
    return CandidateService(repo=InMemoryCandidateRepo())


def _create(svc, email="ivan@example.com"):
    return svc.create(CandidateCreateDTO(
        first_name="Ivan", last_name="Franko", email=email,
    ))


def test_create_candidate(service):
    c = _create(service)
    assert c.id == 1
    assert c.status == "NEW"


def test_duplicate_email_raises_conflict(service):
    _create(service)
    with pytest.raises(ConflictError):
        _create(service)


def test_allowed_status_transition_writes_history(service):
    c = _create(service)
    # signal публікується, але receiver імпортує Celery; для unit-test глушимо
    with patch("apps.candidates.signals.candidate_status_changed.send"):
        updated = service.change_status(c.id, "SCREENING", changed_by_id=42)
    assert updated.status == "SCREENING"
    history = service._repo._history  # type: ignore[attr-defined]
    assert history == [{
        "candidate_id": c.id,
        "from_status": "NEW", "to_status": "SCREENING",
        "changed_by_id": 42,
    }]


def test_forbidden_transition_raises(service):
    c = _create(service)
    with pytest.raises(ValidationError):
        service.change_status(c.id, "HIRED")  # NEW -> HIRED заборонено


def test_unknown_status_raises(service):
    c = _create(service)
    with pytest.raises(ValidationError):
        service.change_status(c.id, "INVALID")


def test_get_missing_raises_not_found(service):
    with pytest.raises(NotFoundError):
        service.get(9999)


def test_change_status_idempotent(service):
    c = _create(service)
    with patch("apps.candidates.signals.candidate_status_changed.send"):
        same = service.change_status(c.id, "NEW")
    assert same.status == "NEW"
