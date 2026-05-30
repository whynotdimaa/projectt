"""
Integration tests for /api/v1/candidates/ endpoints.
Uses real DB via @pytest.mark.django_db + DRF APIClient with JWT.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.django_db

CANDIDATES_URL = "/api/v1/candidates/"


def _candidate_payload(**kw):
    defaults = {"first_name": "Ivan", "last_name": "Franko", "email": "ivan@test.com"}
    return {**defaults, **kw}


class TestCandidateAuth:
    def test_anon_cannot_list(self, anon_client):
        assert anon_client.get(CANDIDATES_URL).status_code == 401

    def test_anon_cannot_create(self, anon_client):
        assert anon_client.post(CANDIDATES_URL, _candidate_payload(), format="json").status_code == 401

    def test_interviewer_can_list(self, interviewer_client):
        assert interviewer_client.get(CANDIDATES_URL).status_code == 200

    def test_interviewer_cannot_create(self, interviewer_client):
        assert interviewer_client.post(CANDIDATES_URL, _candidate_payload(), format="json").status_code == 403


class TestCandidateList:
    def test_list_empty(self, recruiter_client):
        resp = recruiter_client.get(CANDIDATES_URL)
        assert resp.status_code == 200
        assert resp.data == []

    def test_list_returns_created(self, recruiter_client):
        recruiter_client.post(CANDIDATES_URL, _candidate_payload(), format="json")
        resp = recruiter_client.get(CANDIDATES_URL)
        assert len(resp.data) == 1

    def test_list_filter_by_status(self, recruiter_client):
        recruiter_client.post(CANDIDATES_URL, _candidate_payload(email="a@t.com"), format="json")
        recruiter_client.post(CANDIDATES_URL, _candidate_payload(email="b@t.com"), format="json")
        resp = recruiter_client.get(CANDIDATES_URL + "?status=NEW")
        assert len(resp.data) == 2

    def test_list_filter_by_search(self, recruiter_client):
        recruiter_client.post(CANDIDATES_URL, _candidate_payload(email="unique123@t.com"), format="json")
        recruiter_client.post(CANDIDATES_URL, _candidate_payload(email="other@t.com"), format="json")
        resp = recruiter_client.get(CANDIDATES_URL + "?search=unique123")
        assert len(resp.data) == 1


class TestCandidateCreate:
    def test_create_returns_201(self, recruiter_client):
        assert recruiter_client.post(CANDIDATES_URL, _candidate_payload(), format="json").status_code == 201

    def test_create_sets_new_status(self, recruiter_client):
        resp = recruiter_client.post(CANDIDATES_URL, _candidate_payload(), format="json")
        assert resp.data["status"] == "NEW"

    def test_create_returns_id(self, recruiter_client):
        resp = recruiter_client.post(CANDIDATES_URL, _candidate_payload(), format="json")
        assert resp.data["id"] > 0

    def test_create_stores_all_fields(self, recruiter_client):
        payload = _candidate_payload(phone="+380991234567", desired_position="Dev")
        resp = recruiter_client.post(CANDIDATES_URL, payload, format="json")
        assert resp.data["phone"] == "+380991234567"
        assert resp.data["desired_position"] == "Dev"

    def test_create_duplicate_email_returns_409(self, recruiter_client):
        recruiter_client.post(CANDIDATES_URL, _candidate_payload(), format="json")
        assert recruiter_client.post(CANDIDATES_URL, _candidate_payload(), format="json").status_code == 409

    def test_create_missing_email_returns_400(self, recruiter_client):
        assert recruiter_client.post(CANDIDATES_URL, {"first_name": "A", "last_name": "B"}, format="json").status_code == 400

    def test_create_invalid_email_returns_400(self, recruiter_client):
        assert recruiter_client.post(CANDIDATES_URL, _candidate_payload(email="not-an-email"), format="json").status_code == 400

    def test_create_missing_first_name_returns_400(self, recruiter_client):
        assert recruiter_client.post(CANDIDATES_URL, {"last_name": "B", "email": "x@t.com"}, format="json").status_code == 400


class TestCandidateDetail:
    def _create(self, client):
        return client.post(CANDIDATES_URL, _candidate_payload(), format="json").data["id"]

    def test_get_returns_200(self, recruiter_client):
        cid = self._create(recruiter_client)
        assert recruiter_client.get(f"{CANDIDATES_URL}{cid}/").status_code == 200

    def test_get_missing_returns_404(self, recruiter_client):
        assert recruiter_client.get(f"{CANDIDATES_URL}9999/").status_code == 404

    def test_patch_updates_phone(self, recruiter_client):
        cid = self._create(recruiter_client)
        resp = recruiter_client.patch(f"{CANDIDATES_URL}{cid}/", {"phone": "+380001234567"}, format="json")
        assert resp.status_code == 200
        assert resp.data["phone"] == "+380001234567"

    def test_patch_partial_preserves_others(self, recruiter_client):
        cid = self._create(recruiter_client)
        recruiter_client.patch(f"{CANDIDATES_URL}{cid}/", {"phone": "111"}, format="json")
        assert recruiter_client.get(f"{CANDIDATES_URL}{cid}/").data["first_name"] == "Ivan"

    def test_delete_returns_204(self, recruiter_client):
        cid = self._create(recruiter_client)
        assert recruiter_client.delete(f"{CANDIDATES_URL}{cid}/").status_code == 204

    def test_delete_then_get_returns_404(self, recruiter_client):
        cid = self._create(recruiter_client)
        recruiter_client.delete(f"{CANDIDATES_URL}{cid}/")
        assert recruiter_client.get(f"{CANDIDATES_URL}{cid}/").status_code == 404

    def test_interviewer_cannot_delete(self, recruiter_client, interviewer_client):
        cid = self._create(recruiter_client)
        assert interviewer_client.delete(f"{CANDIDATES_URL}{cid}/").status_code == 403


class TestCandidateStatusChange:
    def _create(self, client):
        return client.post(CANDIDATES_URL, _candidate_payload(), format="json").data["id"]

    def test_allowed_transition_returns_200(self, recruiter_client):
        cid = self._create(recruiter_client)
        resp = recruiter_client.patch(f"{CANDIDATES_URL}{cid}/status/", {"status": "SCREENING"}, format="json")
        assert resp.status_code == 200
        assert resp.data["status"] == "SCREENING"

    def test_forbidden_transition_returns_400(self, recruiter_client):
        cid = self._create(recruiter_client)
        assert recruiter_client.patch(f"{CANDIDATES_URL}{cid}/status/", {"status": "HIRED"}, format="json").status_code == 400

    def test_invalid_status_returns_400(self, recruiter_client):
        cid = self._create(recruiter_client)
        assert recruiter_client.patch(f"{CANDIDATES_URL}{cid}/status/", {"status": "ZOMBIE"}, format="json").status_code == 400

    def test_missing_status_field_returns_400(self, recruiter_client):
        cid = self._create(recruiter_client)
        assert recruiter_client.patch(f"{CANDIDATES_URL}{cid}/status/", {}, format="json").status_code == 400

    def test_interviewer_cannot_change_status(self, recruiter_client, interviewer_client):
        cid = self._create(recruiter_client)
        assert interviewer_client.patch(f"{CANDIDATES_URL}{cid}/status/", {"status": "SCREENING"}, format="json").status_code == 403

    def test_full_funnel_via_api(self, recruiter_client):
        cid = self._create(recruiter_client)
        for status in ["SCREENING", "INTERVIEW", "OFFER", "HIRED"]:
            resp = recruiter_client.patch(f"{CANDIDATES_URL}{cid}/status/", {"status": status}, format="json")
            assert resp.status_code == 200, f"Failed at {status}: {resp.data}"
        assert resp.data["status"] == "HIRED"

    def test_status_change_missing_candidate(self, recruiter_client):
        assert recruiter_client.patch(f"{CANDIDATES_URL}9999/status/", {"status": "SCREENING"}, format="json").status_code == 404
