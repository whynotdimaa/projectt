"""
DTO для шару сервісів. Чисті dataclass-и, без ORM і без DRF.
Використовуються як вхід/вихід CandidateService.
DRF serializer-и (Крок 3) будуть мапити HTTP <-> DTO.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class CandidateCreateDTO:
    first_name: str
    last_name: str
    email: str
    phone: str = ""
    resume_url: str = ""
    desired_position: str = ""


@dataclass(frozen=True)
class CandidateUpdateDTO:
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    resume_url: str | None = None
    desired_position: str | None = None


@dataclass(frozen=True)
class CandidateDTO:
    id: int
    first_name: str
    last_name: str
    email: str
    phone: str
    resume_url: str
    desired_position: str
    status: str
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class CandidateFilterDTO:
    status: str | None = None
    search: str | None = None  # пошук по імені / email
