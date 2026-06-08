from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable

from ..dto import VacancyCreateDTO, VacancyDTO, VacancyFilterDTO


class IVacancyRepository(ABC):
    @abstractmethod
    def get_by_id(self, vacancy_id: int) -> VacancyDTO | None: ...

    @abstractmethod
    def list(self, filters: VacancyFilterDTO) -> Iterable[VacancyDTO]: ...

    @abstractmethod
    def add(self, data: VacancyCreateDTO) -> VacancyDTO: ...

    @abstractmethod
    def close(self, vacancy_id: int) -> VacancyDTO: ...

    @abstractmethod
    def delete(self, vacancy_id: int) -> None: ...
