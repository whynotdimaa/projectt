from ..repositories.vacancy_repository import VacancyRepository
from .vacancy_service import VacancyService


def get_vacancy_service() -> VacancyService:
    return VacancyService(repo=VacancyRepository())
