from __future__ import annotations

from typing import Iterable

from django.utils import timezone

from core.exceptions import NotFoundError

from ..dto import VacancyCreateDTO, VacancyDTO, VacancyFilterDTO
from ..models import Vacancy
from .interfaces import IVacancyRepository


def _to_dto(o: Vacancy) -> VacancyDTO:
    return VacancyDTO(
        id=o.id,
        title=o.title,
        department=o.department,
        description=o.description,
        recruiter_id=o.recruiter_id,
        is_open=o.is_open,
        created_at=o.created_at,
        closed_at=o.closed_at,
    )


class VacancyRepository(IVacancyRepository):
    def get_by_id(self, vacancy_id: int) -> VacancyDTO | None:
        o = Vacancy.objects.filter(pk=vacancy_id).first()
        return _to_dto(o) if o else None

    def list(self, filters: VacancyFilterDTO) -> Iterable[VacancyDTO]:
        qs = Vacancy.objects.all()
        if filters.is_open is not None:
            qs = qs.filter(is_open=filters.is_open)
        if filters.recruiter_id is not None:
            qs = qs.filter(recruiter_id=filters.recruiter_id)
        return [_to_dto(o) for o in qs]

    def add(self, data: VacancyCreateDTO) -> VacancyDTO:
        o = Vacancy.objects.create(
            title=data.title,
            department=data.department,
            description=data.description,
            recruiter_id=data.recruiter_id,
        )
        return _to_dto(o)

    def close(self, vacancy_id: int) -> VacancyDTO:
        o = Vacancy.objects.filter(pk=vacancy_id).first()
        if not o:
            raise NotFoundError(f"Vacancy {vacancy_id} not found")
        if o.is_open:
            o.is_open = False
            o.closed_at = timezone.now()
            o.save(update_fields=("is_open", "closed_at"))
        return _to_dto(o)

    def delete(self, vacancy_id: int) -> None:
        deleted, _ = Vacancy.objects.filter(pk=vacancy_id).delete()
        if not deleted:
            raise NotFoundError(f"Vacancy {vacancy_id} not found")
