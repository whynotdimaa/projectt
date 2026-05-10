from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


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
    score: Optional[int]
    comment: str
    created_at: datetime
    evaluated_at: Optional[datetime]


@dataclass(frozen=True)
class InterviewFilterDTO:
    candidate_id: Optional[int] = None
    interviewer_id: Optional[int] = None
