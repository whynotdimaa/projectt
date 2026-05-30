"""
Unit tests for CandidateStatus enums and ALLOWED_TRANSITIONS.
Tests ALL possible transition combinations (allowed + forbidden).
"""
import pytest

from apps.candidates.enums import (
    ALLOWED_TRANSITIONS,
    CandidateStatus,
    is_transition_allowed,
)


class TestAllowedTransitions:
    """Test every cell of the transition matrix."""

    # ── allowed transitions ──
    def test_new_to_screening(self):
        assert is_transition_allowed("NEW", "SCREENING") is True

    def test_new_to_rejected(self):
        assert is_transition_allowed("NEW", "REJECTED") is True

    def test_screening_to_interview(self):
        assert is_transition_allowed("SCREENING", "INTERVIEW") is True

    def test_screening_to_rejected(self):
        assert is_transition_allowed("SCREENING", "REJECTED") is True

    def test_interview_to_offer(self):
        assert is_transition_allowed("INTERVIEW", "OFFER") is True

    def test_interview_to_rejected(self):
        assert is_transition_allowed("INTERVIEW", "REJECTED") is True

    def test_offer_to_hired(self):
        assert is_transition_allowed("OFFER", "HIRED") is True

    def test_offer_to_rejected(self):
        assert is_transition_allowed("OFFER", "REJECTED") is True

    # ── forbidden transitions ──
    def test_new_to_interview_forbidden(self):
        assert is_transition_allowed("NEW", "INTERVIEW") is False

    def test_new_to_offer_forbidden(self):
        assert is_transition_allowed("NEW", "OFFER") is False

    def test_new_to_hired_forbidden(self):
        assert is_transition_allowed("NEW", "HIRED") is False

    def test_screening_to_offer_forbidden(self):
        assert is_transition_allowed("SCREENING", "OFFER") is False

    def test_screening_to_hired_forbidden(self):
        assert is_transition_allowed("SCREENING", "HIRED") is False

    def test_interview_to_hired_forbidden(self):
        assert is_transition_allowed("INTERVIEW", "HIRED") is False

    def test_hired_to_anything_forbidden(self):
        for status in CandidateStatus.values:
            assert is_transition_allowed("HIRED", status) is False

    def test_rejected_to_anything_forbidden(self):
        for status in CandidateStatus.values:
            assert is_transition_allowed("REJECTED", status) is False

    def test_unknown_from_status(self):
        assert is_transition_allowed("UNKNOWN", "NEW") is False

    def test_unknown_to_status(self):
        assert is_transition_allowed("NEW", "UNKNOWN") is False

    def test_self_transition_new(self):
        assert is_transition_allowed("NEW", "NEW") is False

    def test_self_transition_screening(self):
        assert is_transition_allowed("SCREENING", "SCREENING") is False


class TestCandidateStatusEnum:
    def test_all_values_present(self):
        values = set(CandidateStatus.values)
        assert "NEW" in values
        assert "SCREENING" in values
        assert "INTERVIEW" in values
        assert "OFFER" in values
        assert "HIRED" in values
        assert "REJECTED" in values

    def test_choices_have_labels(self):
        for value, label in CandidateStatus.choices:
            assert label  # non-empty

    def test_allowed_transitions_covers_all_statuses(self):
        for status in CandidateStatus.values:
            assert status in ALLOWED_TRANSITIONS

    def test_terminal_states_have_empty_transitions(self):
        assert ALLOWED_TRANSITIONS["HIRED"] == set()
        assert ALLOWED_TRANSITIONS["REJECTED"] == set()
