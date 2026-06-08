from __future__ import annotations

from typing import Iterable

from django.utils import timezone

from core.exceptions import NotFoundError

from ..dto import (
    InterviewCreateDTO,
    InterviewDTO,
    InterviewEvaluateDTO,
    InterviewFilterDTO,
)
from ..models import Interview
from .interfaces import IInterviewRepository


def _to_dto(o: Interview) -> InterviewDTO:
    return InterviewDTO(
        id=o.id,
        candidate_id=o.candidate_id,
        recruiter_id=o.recruiter_id,
        interviewer_id=o.interviewer_id,
        scheduled_at=o.scheduled_at,
        score=o.score,
        comment=o.comment,
        created_at=o.created_at,
        evaluated_at=o.evaluated_at,
    )


class InterviewRepository(IInterviewRepository):
    def get_by_id(self, interview_id: int) -> InterviewDTO | None:
        o = Interview.objects.filter(pk=interview_id).first()
        return _to_dto(o) if o else None

    def list(self, filters: InterviewFilterDTO) -> Iterable[InterviewDTO]:
        qs = Interview.objects.all()
        if filters.candidate_id is not None:
            qs = qs.filter(candidate_id=filters.candidate_id)
        if filters.interviewer_id is not None:
            qs = qs.filter(interviewer_id=filters.interviewer_id)
        return [_to_dto(o) for o in qs]

    def add(self, data: InterviewCreateDTO) -> InterviewDTO:
        o = Interview.objects.create(
            candidate_id=data.candidate_id,
            recruiter_id=data.recruiter_id,
            interviewer_id=data.interviewer_id,
            scheduled_at=data.scheduled_at,
        )
        return _to_dto(o)

    def evaluate(self, interview_id: int, data: InterviewEvaluateDTO) -> InterviewDTO:
        o = Interview.objects.filter(pk=interview_id).first()
        if not o:
            raise NotFoundError(f"Interview {interview_id} not found")
        o.score = data.score
        o.comment = data.comment
        o.evaluated_at = timezone.now()
        o.save(update_fields=("score", "comment", "evaluated_at"))
        return _to_dto(o)

    def delete(self, interview_id: int) -> None:
        deleted, _ = Interview.objects.filter(pk=interview_id).delete()
        if not deleted:
            raise NotFoundError(f"Interview {interview_id} not found")
