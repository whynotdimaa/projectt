"""
Контракт репозиторію кандидатів.
Сервіс залежить ВИКЛЮЧНО від цього інтерфейсу (Dependency Inversion).
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable, Optional

from ..dto import CandidateCreateDTO, CandidateDTO, CandidateFilterDTO, CandidateUpdateDTO


class ICandidateRepository(ABC):
    @abstractmethod
    def get_by_id(self, candidate_id: int) -> Optional[CandidateDTO]: ...

    @abstractmethod
    def get_by_email(self, email: str) -> Optional[CandidateDTO]: ...

    @abstractmethod
    def list(self, filters: CandidateFilterDTO) -> Iterable[CandidateDTO]: ...

    @abstractmethod
    def add(self, data: CandidateCreateDTO) -> CandidateDTO: ...

    @abstractmethod
    def update(self, candidate_id: int, data: CandidateUpdateDTO) -> CandidateDTO: ...

    @abstractmethod
    def update_status(self, candidate_id: int, new_status: str) -> CandidateDTO: ...

    @abstractmethod
    def delete(self, candidate_id: int) -> None: ...
