"""
Enum статусів кандидата + дозволені переходи воронки.
NEW -> SCREENING -> INTERVIEW -> OFFER -> HIRED / REJECTED
REJECTED доступний з будь-якого активного статусу.
"""
from __future__ import annotations

from django.db import models


class CandidateStatus(models.TextChoices):
    NEW = "NEW", "New"
    SCREENING = "SCREENING", "Screening"
    INTERVIEW = "INTERVIEW", "Interview"
    OFFER = "OFFER", "Offer"
    HIRED = "HIRED", "Hired"
    REJECTED = "REJECTED", "Rejected"


# Дозволені переходи. Використовуватиметься у CandidateService (Крок 2).
ALLOWED_TRANSITIONS: dict[str, set[str]] = {
    CandidateStatus.NEW: {CandidateStatus.SCREENING, CandidateStatus.REJECTED},
    CandidateStatus.SCREENING: {CandidateStatus.INTERVIEW, CandidateStatus.REJECTED},
    CandidateStatus.INTERVIEW: {CandidateStatus.OFFER, CandidateStatus.REJECTED},
    CandidateStatus.OFFER: {CandidateStatus.HIRED, CandidateStatus.REJECTED},
    CandidateStatus.HIRED: set(),
    CandidateStatus.REJECTED: set(),
}


def is_transition_allowed(from_status: str, to_status: str) -> bool:
    """Return True only if the transition from_status → to_status is in ALLOWED_TRANSITIONS."""
    allowed = ALLOWED_TRANSITIONS.get(from_status)
    if allowed is None:
        return False  # unknown from_status
    return to_status in allowed
