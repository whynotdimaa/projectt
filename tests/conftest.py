"""
Shared fixtures for all tests.
Unit fixtures: InMemory repos (no DB).
Integration fixtures: real DB via @pytest.mark.django_db + DRF APIClient.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Iterable, Optional
from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.candidates.dto import (
    CandidateCreateDTO,
    CandidateDTO,
    CandidateFilterDTO,
    CandidateUpdateDTO,
)
from apps.candidates.repositories.interfaces import ICandidateRepository
from apps.candidates.services.candidate_service import CandidateService
from apps.interviews.dto import (
    InterviewCreateDTO,
    InterviewDTO,
    InterviewEvaluateDTO,
    InterviewFilterDTO,
)
from apps.interviews.repositories.interfaces import IInterviewRepository
from apps.interviews.services.interview_service import InterviewService
from apps.users.enums import UserRole
from apps.vacancies.dto import (
    VacancyCreateDTO,
    VacancyDTO,
    VacancyFilterDTO,
)
from apps.vacancies.repositories.interfaces import IVacancyRepository
from apps.vacancies.services.vacancy_service import VacancyService
from core.exceptions import NotFoundError

User = get_user_model()


# ─────────────────────────────────────────────
#  InMemory Repositories (unit tests, no DB)
# ─────────────────────────────────────────────

def _now() -> datetime:
    return datetime.now(timezone.utc)


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
        if filters.search:
            t = filters.search.lower()
            items = [
                c for c in items
                if t in c.first_name.lower() or t in c.last_name.lower() or t in c.email.lower()
            ]
        return items

    def add(self, data: CandidateCreateDTO) -> CandidateDTO:
        now = _now()
        dto = CandidateDTO(
            id=self._next_id,
            first_name=data.first_name,
            last_name=data.last_name,
            email=data.email,
            phone=data.phone,
            resume_url=data.resume_url,
            desired_position=data.desired_position,
            status="NEW",
            created_at=now,
            updated_at=now,
        )
        self._store[self._next_id] = dto
        self._next_id += 1
        return dto

    def update(self, candidate_id: int, data: CandidateUpdateDTO) -> CandidateDTO:
        c = self._store.get(candidate_id)
        if not c:
            raise NotFoundError(f"Candidate {candidate_id} not found")
        fields = {
            "first_name": data.first_name or c.first_name,
            "last_name": data.last_name or c.last_name,
            "phone": data.phone if data.phone is not None else c.phone,
            "resume_url": data.resume_url if data.resume_url is not None else c.resume_url,
            "desired_position": data.desired_position if data.desired_position is not None else c.desired_position,
        }
        updated = CandidateDTO(**{**c.__dict__, **fields, "updated_at": _now()})
        self._store[candidate_id] = updated
        return updated

    def update_status(self, candidate_id: int, new_status: str) -> CandidateDTO:
        c = self._store[candidate_id]
        updated = CandidateDTO(**{**c.__dict__, "status": new_status, "updated_at": _now()})
        self._store[candidate_id] = updated
        return updated

    def add_status_history(self, candidate_id, from_status, to_status, changed_by_id) -> None:
        self._history.append({
            "candidate_id": candidate_id,
            "from_status": from_status,
            "to_status": to_status,
            "changed_by_id": changed_by_id,
        })

    def delete(self, candidate_id: int) -> None:
        if candidate_id not in self._store:
            raise NotFoundError(f"Candidate {candidate_id} not found")
        del self._store[candidate_id]


class InMemoryInterviewRepo(IInterviewRepository):
    def __init__(self) -> None:
        self._store: dict[int, InterviewDTO] = {}
        self._next_id = 1

    def get_by_id(self, interview_id: int) -> Optional[InterviewDTO]:
        return self._store.get(interview_id)

    def list(self, filters: InterviewFilterDTO) -> Iterable[InterviewDTO]:
        items = list(self._store.values())
        if filters.candidate_id is not None:
            items = [i for i in items if i.candidate_id == filters.candidate_id]
        if filters.interviewer_id is not None:
            items = [i for i in items if i.interviewer_id == filters.interviewer_id]
        return items

    def add(self, data: InterviewCreateDTO) -> InterviewDTO:
        now = _now()
        dto = InterviewDTO(
            id=self._next_id,
            candidate_id=data.candidate_id,
            recruiter_id=data.recruiter_id,
            interviewer_id=data.interviewer_id,
            scheduled_at=data.scheduled_at,
            score=None,
            comment="",
            created_at=now,
            evaluated_at=None,
        )
        self._store[self._next_id] = dto
        self._next_id += 1
        return dto

    def evaluate(self, interview_id: int, data: InterviewEvaluateDTO) -> InterviewDTO:
        i = self._store.get(interview_id)
        if not i:
            raise NotFoundError(f"Interview {interview_id} not found")
        updated = InterviewDTO(**{**i.__dict__, "score": data.score, "comment": data.comment, "evaluated_at": _now()})
        self._store[interview_id] = updated
        return updated

    def delete(self, interview_id: int) -> None:
        if interview_id not in self._store:
            raise NotFoundError(f"Interview {interview_id} not found")
        del self._store[interview_id]


class InMemoryVacancyRepo(IVacancyRepository):
    def __init__(self) -> None:
        self._store: dict[int, VacancyDTO] = {}
        self._next_id = 1

    def get_by_id(self, vacancy_id: int) -> Optional[VacancyDTO]:
        return self._store.get(vacancy_id)

    def list(self, filters: VacancyFilterDTO) -> Iterable[VacancyDTO]:
        items = list(self._store.values())
        if filters.is_open is not None:
            items = [v for v in items if v.is_open == filters.is_open]
        if filters.recruiter_id is not None:
            items = [v for v in items if v.recruiter_id == filters.recruiter_id]
        return items

    def add(self, data: VacancyCreateDTO) -> VacancyDTO:
        dto = VacancyDTO(
            id=self._next_id,
            title=data.title,
            department=data.department,
            description=data.description,
            recruiter_id=data.recruiter_id,
            is_open=True,
            created_at=_now(),
            closed_at=None,
        )
        self._store[self._next_id] = dto
        self._next_id += 1
        return dto

    def close(self, vacancy_id: int) -> VacancyDTO:
        v = self._store.get(vacancy_id)
        if not v:
            raise NotFoundError(f"Vacancy {vacancy_id} not found")
        closed = VacancyDTO(**{**v.__dict__, "is_open": False, "closed_at": _now()})
        self._store[vacancy_id] = closed
        return closed

    def delete(self, vacancy_id: int) -> None:
        if vacancy_id not in self._store:
            raise NotFoundError(f"Vacancy {vacancy_id} not found")
        del self._store[vacancy_id]


# ─────────────────────────────────────────────
#  Service fixtures (unit)
# ─────────────────────────────────────────────

@pytest.fixture
def candidate_repo():
    return InMemoryCandidateRepo()


@pytest.fixture
def candidate_service(candidate_repo):
    return CandidateService(repo=candidate_repo)


@pytest.fixture
def interview_repo():
    return InMemoryInterviewRepo()


@pytest.fixture
def interview_service(interview_repo):
    return InterviewService(repo=interview_repo)


@pytest.fixture
def vacancy_repo():
    return InMemoryVacancyRepo()


@pytest.fixture
def vacancy_service(vacancy_repo):
    return VacancyService(repo=InMemoryVacancyRepo())


# ─────────────────────────────────────────────
#  DB user fixtures (integration tests)
# ─────────────────────────────────────────────

@pytest.fixture
def recruiter_user(db):
    return User.objects.create_user(
        email="recruiter@test.com",
        password="testpass123",
        role=UserRole.RECRUITER,
        first_name="Test",
        last_name="Recruiter",
        username="recruiter@test.com",
    )


@pytest.fixture
def interviewer_user(db):
    return User.objects.create_user(
        email="interviewer@test.com",
        password="testpass123",
        role=UserRole.INTERVIEWER,
        first_name="Test",
        last_name="Interviewer",
        username="interviewer@test.com",
    )


@pytest.fixture
def admin_user(db):
    return User.objects.create_user(
        email="admin@test.com",
        password="testpass123",
        role=UserRole.ADMIN,
        first_name="Test",
        last_name="Admin",
        username="admin@test.com",
    )


def _get_token(client, email, password):
    resp = client.post("/api/v1/auth/login/", {"email": email, "password": password}, format="json")
    return resp.data["access"]


@pytest.fixture
def recruiter_client(recruiter_user):
    client = APIClient()
    token = _get_token(client, "recruiter@test.com", "testpass123")
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return client


@pytest.fixture
def interviewer_client(interviewer_user):
    client = APIClient()
    token = _get_token(client, "interviewer@test.com", "testpass123")
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return client


@pytest.fixture
def admin_client(admin_user):
    client = APIClient()
    token = _get_token(client, "admin@test.com", "testpass123")
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return client


@pytest.fixture
def anon_client():
    return APIClient()


# ─────────────────────────────────────────────
#  Helper: patch signal send (unit tests)
# ─────────────────────────────────────────────

@pytest.fixture
def no_signal():
    """Suppress candidate_status_changed signal for unit tests."""
    with patch("apps.candidates.signals.candidate_status_changed.send"):
        yield
