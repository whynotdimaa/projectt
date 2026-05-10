from __future__ import annotations

from typing import Iterable

from core.exceptions import NotFoundError, ValidationError

from ..dto import (
    InterviewCreateDTO,
    InterviewDTO,
    InterviewEvaluateDTO,
    InterviewFilterDTO,
)
from ..repositories.interfaces import IInterviewRepository


class InterviewService:
    def __init__(self, repo: IInterviewRepository) -> None:
        self._repo = repo

    def get(self, interview_id: int) -> InterviewDTO:
        item = self._repo.get_by_id(interview_id)
        if not item:
            raise NotFoundError(f"Interview {interview_id} not found")
        return item

    def list(self, filters: InterviewFilterDTO) -> Iterable[InterviewDTO]:
        return self._repo.list(filters)

    def schedule(self, data: InterviewCreateDTO) -> InterviewDTO:
        return self._repo.add(data)

    def evaluate(self, interview_id: int, data: InterviewEvaluateDTO) -> InterviewDTO:
        if not (1 <= data.score <= 10):
            raise ValidationError("Score must be in range 1..10")
        return self._repo.evaluate(interview_id, data)

    def delete(self, interview_id: int) -> None:
        self._repo.delete(interview_id)
