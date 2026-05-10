"""
Composition root для CandidateService.

У Кроці 3 в'юшки DRF викликають get_candidate_service() — це єдина точка,
де "склеюються" реалізації репозиторію та сервісу. Заміна реалізації
(наприклад, mock у тестах) робиться тут, не змінюючи решту коду.
"""
from __future__ import annotations

from ..repositories.candidate_repository import CandidateRepository
from .candidate_service import CandidateService


def get_candidate_service() -> CandidateService:
    return CandidateService(repo=CandidateRepository())
