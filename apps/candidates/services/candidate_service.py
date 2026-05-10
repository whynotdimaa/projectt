"""
CandidateService — Business Logic Layer.

Відповідає за:
- CRUD з валідацією доменних інваріантів (унікальний email, тощо)
- зміну статусу з перевіркою дозволеного переходу (`is_transition_allowed`)
- викидання доменних виключень (NotFoundError / ValidationError / ConflictError)

НЕ знає про:
- HTTP / DRF
- Django ORM (працює лише з ICandidateRepository та DTO)

DI: репозиторій передається в конструктор. У Кроці 3 фабрика
сервісу створюватиметься у DRF-в'юшках через `get_candidate_service()`.
"""
from __future__ import annotations

from typing import Iterable

from core.exceptions import ConflictError, NotFoundError, ValidationError

from ..dto import (
    CandidateCreateDTO,
    CandidateDTO,
    CandidateFilterDTO,
    CandidateUpdateDTO,
)
from ..enums import CandidateStatus, is_transition_allowed
from ..repositories.interfaces import ICandidateRepository


class CandidateService:
    def __init__(self, repo: ICandidateRepository) -> None:
        self._repo = repo

    # ---------- read ----------
    def get(self, candidate_id: int) -> CandidateDTO:
        candidate = self._repo.get_by_id(candidate_id)
        if not candidate:
            raise NotFoundError(f"Candidate {candidate_id} not found")
        return candidate

    def list(self, filters: CandidateFilterDTO) -> Iterable[CandidateDTO]:
        if filters.status and filters.status not in CandidateStatus.values:
            raise ValidationError(f"Unknown status: {filters.status}")
        return self._repo.list(filters)

    # ---------- write ----------
    def create(self, data: CandidateCreateDTO) -> CandidateDTO:
        if self._repo.get_by_email(data.email):
            raise ConflictError(f"Candidate with email {data.email} already exists")
        return self._repo.add(data)

    def update(self, candidate_id: int, data: CandidateUpdateDTO) -> CandidateDTO:
        # перевірка існування — у репо (NotFoundError)
        return self._repo.update(candidate_id, data)

    def delete(self, candidate_id: int) -> None:
        self._repo.delete(candidate_id)

    # ---------- status transitions ----------
    def change_status(
        self,
        candidate_id: int,
        new_status: str,
        changed_by_id: int | None = None,
    ) -> CandidateDTO:
        if new_status not in CandidateStatus.values:
            raise ValidationError(f"Unknown status: {new_status}")

        current = self._repo.get_by_id(candidate_id)
        if not current:
            raise NotFoundError(f"Candidate {candidate_id} not found")

        if current.status == new_status:
            return current  # idempotent

        if not is_transition_allowed(current.status, new_status):
            raise ValidationError(
                f"Transition {current.status} -> {new_status} is not allowed"
            )

        updated = self._repo.update_status(candidate_id, new_status)
        self._repo.add_status_history(
            candidate_id=candidate_id,
            from_status=current.status,
            to_status=new_status,
            changed_by_id=changed_by_id,
        )
        # Асинхронне сповіщення кандидата (Celery + Strategy pattern).
        # Імпорт всередині методу — щоб уникнути циклу залежностей між apps.
        from apps.notifications.tasks import notify_candidate_status_changed
        notify_candidate_status_changed.delay(
            candidate_email=updated.email,
            candidate_name=f"{updated.first_name} {updated.last_name}",
            from_status=current.status,
            to_status=new_status,
        )
        return updated
