from __future__ import annotations

from typing import Iterable

from core.exceptions import NotFoundError

from ..dto import VacancyCreateDTO, VacancyDTO, VacancyFilterDTO
from ..repositories.interfaces import IVacancyRepository


class VacancyService:
    def __init__(self, repo: IVacancyRepository) -> None:
        self._repo = repo

    def get(self, vacancy_id: int) -> VacancyDTO:
        v = self._repo.get_by_id(vacancy_id)
        if not v:
            raise NotFoundError(f"Vacancy {vacancy_id} not found")
        return v

    def list(self, filters: VacancyFilterDTO) -> Iterable[VacancyDTO]:
        return self._repo.list(filters)

    def create(self, data: VacancyCreateDTO) -> VacancyDTO:
        return self._repo.add(data)

    def close(self, vacancy_id: int) -> VacancyDTO:
        return self._repo.close(vacancy_id)

    def delete(self, vacancy_id: int) -> None:
        self._repo.delete(vacancy_id)
