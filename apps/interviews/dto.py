from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class InterviewCreateDTO:
    candidate_id: int
    recruiter_id: int
    interviewer_id: int
    scheduled_at: datetime


@dataclass(frozen=True)
class InterviewEvaluateDTO:
    score: int
    comment: str = ""


@dataclass(frozen=True)
class InterviewDTO:
    id: int
    candidate_id: int
    recruiter_id: int
    interviewer_id: int
    scheduled_at: datetime
    score: int | None
    comment: str
    created_at: datetime
    evaluated_at: datetime | None


@dataclass(frozen=True)
class InterviewFilterDTO:
    candidate_id: int | None = None
    interviewer_id: int | None = None
