"""
Конкретна реалізація ICandidateRepository поверх Django ORM.
ЄДИНЕ місце, де згадується модель Candidate і ORM-операції.
"""
from __future__ import annotations

from typing import Iterable, Optional

from django.db.models import Q

from core.exceptions import NotFoundError

from ..dto import (
    CandidateCreateDTO,
    CandidateDTO,
    CandidateFilterDTO,
    CandidateUpdateDTO,
)
from ..models import Candidate, StatusHistory
from .interfaces import ICandidateRepository


def _to_dto(obj: Candidate) -> CandidateDTO:
    return CandidateDTO(
        id=obj.id,
        first_name=obj.first_name,
        last_name=obj.last_name,
        email=obj.email,
        phone=obj.phone,
        resume_url=obj.resume_url,
        desired_position=obj.desired_position,
        status=obj.status,
        created_at=obj.created_at,
        updated_at=obj.updated_at,
    )


class CandidateRepository(ICandidateRepository):
    def get_by_id(self, candidate_id: int) -> Optional[CandidateDTO]:
        obj = Candidate.objects.filter(pk=candidate_id).first()
        return _to_dto(obj) if obj else None

    def get_by_email(self, email: str) -> Optional[CandidateDTO]:
        obj = Candidate.objects.filter(email__iexact=email).first()
        return _to_dto(obj) if obj else None

    def list(self, filters: CandidateFilterDTO) -> Iterable[CandidateDTO]:
        qs = Candidate.objects.all()
        if filters.status:
            qs = qs.filter(status=filters.status)
        if filters.search:
            term = filters.search
            qs = qs.filter(
                Q(first_name__icontains=term)
                | Q(last_name__icontains=term)
                | Q(email__icontains=term)
            )
        return [_to_dto(o) for o in qs]

    def add(self, data: CandidateCreateDTO) -> CandidateDTO:
        obj = Candidate.objects.create(
            first_name=data.first_name,
            last_name=data.last_name,
            email=data.email,
            phone=data.phone,
            resume_url=data.resume_url,
            desired_position=data.desired_position,
        )
        return _to_dto(obj)

    def update(self, candidate_id: int, data: CandidateUpdateDTO) -> CandidateDTO:
        obj = Candidate.objects.filter(pk=candidate_id).first()
        if not obj:
            raise NotFoundError(f"Candidate {candidate_id} not found")

        changed = False
        for field_name in ("first_name", "last_name", "phone", "resume_url", "desired_position"):
            value = getattr(data, field_name)
            if value is not None and value != getattr(obj, field_name):
                setattr(obj, field_name, value)
                changed = True
        if changed:
            obj.save()
        return _to_dto(obj)

    def update_status(self, candidate_id: int, new_status: str) -> CandidateDTO:
        obj = Candidate.objects.filter(pk=candidate_id).first()
        if not obj:
            raise NotFoundError(f"Candidate {candidate_id} not found")
        obj.status = new_status
        obj.save(update_fields=("status", "updated_at"))
        return _to_dto(obj)

    def delete(self, candidate_id: int) -> None:
        deleted, _ = Candidate.objects.filter(pk=candidate_id).delete()
        if not deleted:
            raise NotFoundError(f"Candidate {candidate_id} not found")

    def add_status_history(
        self,
        candidate_id: int,
        from_status: str,
        to_status: str,
        changed_by_id: int | None,
    ) -> None:
        StatusHistory.objects.create(
            candidate_id=candidate_id,
            from_status=from_status,
            to_status=to_status,
            changed_by_id=changed_by_id,
        )
