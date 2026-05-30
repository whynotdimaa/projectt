"""
Extended unit tests for CandidateService.
Covers: CRUD, all status transitions, search/filter, edge cases.
Uses InMemoryCandidateRepo (from conftest) — no DB required.
"""
from __future__ import annotations

import pytest

from apps.candidates.dto import (
    CandidateCreateDTO,
    CandidateFilterDTO,
    CandidateUpdateDTO,
)
from core.exceptions import ConflictError, NotFoundError, ValidationError


# ─── helpers ───

def _create(svc, email="ivan@example.com", first="Ivan", last="Franko"):
    return svc.create(CandidateCreateDTO(first_name=first, last_name=last, email=email))


def _advance(svc, cid, *statuses, changed_by=None):
    """Advance through a chain of status transitions."""
    current = None
    for s in statuses:
        current = svc.change_status(cid, s, changed_by_id=changed_by)
    return current


# ─── create ───

class TestCreate:
    def test_creates_with_new_status(self, candidate_service):
        c = _create(candidate_service)
        assert c.status == "NEW"

    def test_assigns_sequential_ids(self, candidate_service):
        c1 = _create(candidate_service, "a@test.com")
        c2 = _create(candidate_service, "b@test.com")
        assert c2.id == c1.id + 1

    def test_stores_all_fields(self, candidate_service):
        c = candidate_service.create(CandidateCreateDTO(
            first_name="Олена",
            last_name="Коваль",
            email="olena@test.com",
            phone="+380991234567",
            resume_url="https://cv.example.com",
            desired_position="Python Dev",
        ))
        assert c.phone == "+380991234567"
        assert c.desired_position == "Python Dev"

    def test_duplicate_email_raises_conflict(self, candidate_service):
        _create(candidate_service)
        with pytest.raises(ConflictError):
            _create(candidate_service)

    def test_email_case_insensitive_duplicate(self, candidate_service):
        _create(candidate_service, "Ivan@Example.COM")
        with pytest.raises(ConflictError):
            _create(candidate_service, "ivan@example.com")

    def test_optional_fields_default_empty(self, candidate_service):
        c = _create(candidate_service)
        assert c.phone == ""
        assert c.resume_url == ""
        assert c.desired_position == ""


# ─── get ───

class TestGet:
    def test_get_existing(self, candidate_service):
        c = _create(candidate_service)
        fetched = candidate_service.get(c.id)
        assert fetched.email == c.email

    def test_get_missing_raises(self, candidate_service):
        with pytest.raises(NotFoundError):
            candidate_service.get(9999)

    def test_get_negative_id_raises(self, candidate_service):
        with pytest.raises(NotFoundError):
            candidate_service.get(-1)


# ─── list / filter ───

class TestList:
    def test_list_all(self, candidate_service):
        _create(candidate_service, "a@t.com")
        _create(candidate_service, "b@t.com")
        items = list(candidate_service.list(CandidateFilterDTO()))
        assert len(items) == 2

    def test_list_empty(self, candidate_service):
        items = list(candidate_service.list(CandidateFilterDTO()))
        assert items == []

    def test_filter_by_status(self, candidate_service, no_signal):
        c1 = _create(candidate_service, "a@t.com")
        _create(candidate_service, "b@t.com")
        candidate_service.change_status(c1.id, "SCREENING")
        items = list(candidate_service.list(CandidateFilterDTO(status="SCREENING")))
        assert len(items) == 1
        assert items[0].id == c1.id

    def test_filter_by_search_email(self, candidate_service):
        _create(candidate_service, "unique_email@test.com", "Anna", "Smith")
        _create(candidate_service, "other@test.com", "Bob", "Jones")
        items = list(candidate_service.list(CandidateFilterDTO(search="unique_email")))
        assert len(items) == 1

    def test_filter_by_search_name(self, candidate_service):
        _create(candidate_service, "a@t.com", "Іван", "Петренко")
        _create(candidate_service, "b@t.com", "Олена", "Коваль")
        items = list(candidate_service.list(CandidateFilterDTO(search="Іван")))
        assert len(items) == 1

    def test_invalid_status_filter_raises(self, candidate_service):
        with pytest.raises(ValidationError):
            candidate_service.list(CandidateFilterDTO(status="INVALID"))


# ─── update ───

class TestUpdate:
    def test_update_phone(self, candidate_service):
        c = _create(candidate_service)
        updated = candidate_service.update(c.id, CandidateUpdateDTO(phone="+380991111111"))
        assert updated.phone == "+380991111111"

    def test_update_missing_raises(self, candidate_service):
        with pytest.raises(NotFoundError):
            candidate_service.update(9999, CandidateUpdateDTO(phone="123"))

    def test_update_partial_keeps_other_fields(self, candidate_service):
        c = candidate_service.create(CandidateCreateDTO(
            first_name="Ivan", last_name="Franko", email="i@t.com",
            phone="111", desired_position="Dev",
        ))
        updated = candidate_service.update(c.id, CandidateUpdateDTO(phone="999"))
        assert updated.desired_position == "Dev"  # unchanged


# ─── delete ───

class TestDelete:
    def test_delete_existing(self, candidate_service):
        c = _create(candidate_service)
        candidate_service.delete(c.id)
        with pytest.raises(NotFoundError):
            candidate_service.get(c.id)

    def test_delete_missing_raises(self, candidate_service):
        with pytest.raises(NotFoundError):
            candidate_service.delete(9999)

    def test_delete_one_of_many(self, candidate_service):
        c1 = _create(candidate_service, "a@t.com")
        _create(candidate_service, "b@t.com")
        candidate_service.delete(c1.id)
        remaining = list(candidate_service.list(CandidateFilterDTO()))
        assert len(remaining) == 1


# ─── status transitions ───

class TestStatusTransitions:
    def test_new_to_screening(self, candidate_service, no_signal):
        c = _create(candidate_service)
        updated = candidate_service.change_status(c.id, "SCREENING")
        assert updated.status == "SCREENING"

    def test_full_happy_path(self, candidate_service, no_signal):
        c = _create(candidate_service)
        _advance(candidate_service, c.id, "SCREENING", "INTERVIEW", "OFFER", "HIRED")
        final = candidate_service.get(c.id)
        assert final.status == "HIRED"

    def test_rejected_from_new(self, candidate_service, no_signal):
        c = _create(candidate_service)
        updated = candidate_service.change_status(c.id, "REJECTED")
        assert updated.status == "REJECTED"

    def test_rejected_from_screening(self, candidate_service, no_signal):
        c = _create(candidate_service)
        candidate_service.change_status(c.id, "SCREENING")
        updated = candidate_service.change_status(c.id, "REJECTED")
        assert updated.status == "REJECTED"

    def test_forbidden_skip_raises(self, candidate_service):
        c = _create(candidate_service)
        with pytest.raises(ValidationError):
            candidate_service.change_status(c.id, "HIRED")

    def test_hired_is_terminal(self, candidate_service, no_signal):
        c = _create(candidate_service)
        _advance(candidate_service, c.id, "SCREENING", "INTERVIEW", "OFFER", "HIRED")
        with pytest.raises(ValidationError):
            candidate_service.change_status(c.id, "REJECTED")

    def test_rejected_is_terminal(self, candidate_service, no_signal):
        c = _create(candidate_service)
        candidate_service.change_status(c.id, "REJECTED")
        with pytest.raises(ValidationError):
            candidate_service.change_status(c.id, "SCREENING")

    def test_idempotent_same_status_returns_current(self, candidate_service, no_signal):
        c = _create(candidate_service)
        candidate_service.change_status(c.id, "SCREENING")
        same = candidate_service.change_status(c.id, "SCREENING")
        assert same.status == "SCREENING"

    def test_history_recorded_on_transition(self, candidate_service, candidate_repo, no_signal):
        c = _create(candidate_service)
        candidate_service.change_status(c.id, "SCREENING", changed_by_id=42)
        assert len(candidate_repo._history) == 1
        assert candidate_repo._history[0]["from_status"] == "NEW"
        assert candidate_repo._history[0]["to_status"] == "SCREENING"
        assert candidate_repo._history[0]["changed_by_id"] == 42

    def test_idempotent_does_not_add_history(self, candidate_service, candidate_repo, no_signal):
        c = _create(candidate_service)
        candidate_service.change_status(c.id, "NEW")  # same status — idempotent
        assert len(candidate_repo._history) == 0

    def test_change_status_missing_candidate(self, candidate_service):
        with pytest.raises(NotFoundError):
            candidate_service.change_status(9999, "SCREENING")

    def test_unknown_new_status_raises(self, candidate_service):
        c = _create(candidate_service)
        with pytest.raises(ValidationError):
            candidate_service.change_status(c.id, "ZOMBIE")
