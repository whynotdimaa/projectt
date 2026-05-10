from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class VacancyCreateDTO:
    title: str
    recruiter_id: int
    department: str = ""
    description: str = ""


@dataclass(frozen=True)
class VacancyDTO:
    id: int
    title: str
    department: str
    description: str
    recruiter_id: int
    is_open: bool
    created_at: datetime
    closed_at: Optional[datetime]


@dataclass(frozen=True)
class VacancyFilterDTO:
    is_open: Optional[bool] = None
    recruiter_id: Optional[int] = None
