"""
Unit tests for InterviewService and VacancyService.
Uses InMemory repos — no DB.
"""
from __future__ import annotations

from datetime import datetime, timezone

import pytest

from apps.interviews.dto import InterviewCreateDTO, InterviewEvaluateDTO, InterviewFilterDTO
from apps.vacancies.dto import VacancyCreateDTO, VacancyFilterDTO
from core.exceptions import NotFoundError, ValidationError


def _now():
    return datetime.now(timezone.utc)


# ─────────────── InterviewService ───────────────

class TestInterviewServiceSchedule:
    def test_schedule_creates_interview(self, interview_service):
        iv = interview_service.schedule(InterviewCreateDTO(
            candidate_id=1, recruiter_id=10, interviewer_id=20, scheduled_at=_now(),
        ))
        assert iv.id == 1
        assert iv.score is None
        assert iv.evaluated_at is None

    def test_schedule_multiple(self, interview_service):
        interview_service.schedule(InterviewCreateDTO(1, 10, 20, _now()))
        interview_service.schedule(InterviewCreateDTO(2, 10, 21, _now()))
        items = list(interview_service.list(InterviewFilterDTO()))
        assert len(items) == 2

    def test_schedule_stores_correct_ids(self, interview_service):
        iv = interview_service.schedule(InterviewCreateDTO(5, 10, 20, _now()))
        assert iv.candidate_id == 5
        assert iv.recruiter_id == 10
        assert iv.interviewer_id == 20


class TestInterviewServiceGet:
    def test_get_existing(self, interview_service):
        iv = interview_service.schedule(InterviewCreateDTO(1, 10, 20, _now()))
        fetched = interview_service.get(iv.id)
        assert fetched.id == iv.id

    def test_get_missing_raises(self, interview_service):
        with pytest.raises(NotFoundError):
            interview_service.get(9999)


class TestInterviewServiceList:
    def test_list_all(self, interview_service):
        interview_service.schedule(InterviewCreateDTO(1, 10, 20, _now()))
        interview_service.schedule(InterviewCreateDTO(2, 10, 21, _now()))
        assert len(list(interview_service.list(InterviewFilterDTO()))) == 2

    def test_filter_by_candidate(self, interview_service):
        interview_service.schedule(InterviewCreateDTO(1, 10, 20, _now()))
        interview_service.schedule(InterviewCreateDTO(2, 10, 20, _now()))
        items = list(interview_service.list(InterviewFilterDTO(candidate_id=1)))
        assert len(items) == 1

    def test_filter_by_interviewer(self, interview_service):
        interview_service.schedule(InterviewCreateDTO(1, 10, 20, _now()))
        interview_service.schedule(InterviewCreateDTO(1, 10, 21, _now()))
        items = list(interview_service.list(InterviewFilterDTO(interviewer_id=21)))
        assert len(items) == 1

    def test_empty_list(self, interview_service):
        assert list(interview_service.list(InterviewFilterDTO())) == []


class TestInterviewServiceEvaluate:
    def test_evaluate_sets_score(self, interview_service):
        iv = interview_service.schedule(InterviewCreateDTO(1, 10, 20, _now()))
        updated = interview_service.evaluate(iv.id, InterviewEvaluateDTO(score=8, comment="Good"))
        assert updated.score == 8
        assert updated.comment == "Good"
        assert updated.evaluated_at is not None

    def test_evaluate_score_out_of_range_raises(self, interview_service):
        iv = interview_service.schedule(InterviewCreateDTO(1, 10, 20, _now()))
        with pytest.raises(ValidationError):
            interview_service.evaluate(iv.id, InterviewEvaluateDTO(score=11))

    def test_evaluate_score_zero_raises(self, interview_service):
        iv = interview_service.schedule(InterviewCreateDTO(1, 10, 20, _now()))
        with pytest.raises(ValidationError):
            interview_service.evaluate(iv.id, InterviewEvaluateDTO(score=0))

    def test_evaluate_boundary_score_1(self, interview_service):
        iv = interview_service.schedule(InterviewCreateDTO(1, 10, 20, _now()))
        updated = interview_service.evaluate(iv.id, InterviewEvaluateDTO(score=1))
        assert updated.score == 1

    def test_evaluate_boundary_score_10(self, interview_service):
        iv = interview_service.schedule(InterviewCreateDTO(1, 10, 20, _now()))
        updated = interview_service.evaluate(iv.id, InterviewEvaluateDTO(score=10))
        assert updated.score == 10

    def test_evaluate_missing_raises(self, interview_service):
        with pytest.raises(NotFoundError):
            interview_service.evaluate(9999, InterviewEvaluateDTO(score=5))


class TestInterviewServiceDelete:
    def test_delete_removes(self, interview_service):
        iv = interview_service.schedule(InterviewCreateDTO(1, 10, 20, _now()))
        interview_service.delete(iv.id)
        with pytest.raises(NotFoundError):
            interview_service.get(iv.id)

    def test_delete_missing_raises(self, interview_service):
        with pytest.raises(NotFoundError):
            interview_service.delete(9999)


# ─────────────── VacancyService ───────────────

@pytest.fixture
def vsvc(vacancy_repo):
    from apps.vacancies.services.vacancy_service import VacancyService
    return VacancyService(repo=vacancy_repo)


def _vacancy(title="Python Dev", recruiter_id=1, **kw):
    return VacancyCreateDTO(title=title, recruiter_id=recruiter_id, **kw)


class TestVacancyServiceCreate:
    def test_create_returns_open_vacancy(self, vsvc):
        v = vsvc.create(_vacancy())
        assert v.is_open is True
        assert v.closed_at is None

    def test_create_stores_fields(self, vsvc):
        v = vsvc.create(_vacancy("Django Dev", 5, department="Backend"))
        assert v.title == "Django Dev"
        assert v.department == "Backend"
        assert v.recruiter_id == 5


class TestVacancyServiceGet:
    def test_get_existing(self, vsvc):
        v = vsvc.create(_vacancy())
        fetched = vsvc.get(v.id)
        assert fetched.title == v.title

    def test_get_missing_raises(self, vsvc):
        with pytest.raises(NotFoundError):
            vsvc.get(9999)


class TestVacancyServiceList:
    def test_list_all(self, vsvc):
        vsvc.create(_vacancy("A"))
        vsvc.create(_vacancy("B"))
        assert len(list(vsvc.list(VacancyFilterDTO()))) == 2

    def test_filter_open(self, vsvc):
        v = vsvc.create(_vacancy("A"))
        vsvc.create(_vacancy("B"))
        vsvc.close(v.id)
        open_items = list(vsvc.list(VacancyFilterDTO(is_open=True)))
        assert len(open_items) == 1
        assert open_items[0].title == "B"

    def test_filter_closed(self, vsvc):
        v = vsvc.create(_vacancy("A"))
        vsvc.close(v.id)
        closed_items = list(vsvc.list(VacancyFilterDTO(is_open=False)))
        assert len(closed_items) == 1

    def test_filter_by_recruiter(self, vsvc):
        vsvc.create(_vacancy("A", recruiter_id=1))
        vsvc.create(_vacancy("B", recruiter_id=2))
        items = list(vsvc.list(VacancyFilterDTO(recruiter_id=1)))
        assert len(items) == 1


class TestVacancyServiceClose:
    def test_close_sets_flag(self, vsvc):
        v = vsvc.create(_vacancy())
        closed = vsvc.close(v.id)
        assert closed.is_open is False
        assert closed.closed_at is not None

    def test_close_idempotent(self, vsvc):
        v = vsvc.create(_vacancy())
        vsvc.close(v.id)
        again = vsvc.close(v.id)
        assert again.is_open is False

    def test_close_missing_raises(self, vsvc):
        with pytest.raises(NotFoundError):
            vsvc.close(9999)


class TestVacancyServiceDelete:
    def test_delete_removes(self, vsvc):
        v = vsvc.create(_vacancy())
        vsvc.delete(v.id)
        with pytest.raises(NotFoundError):
            vsvc.get(v.id)

    def test_delete_missing_raises(self, vsvc):
        with pytest.raises(NotFoundError):
            vsvc.delete(9999)
