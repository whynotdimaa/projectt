"""
Integration tests for:
- /api/v1/vacancies/
- /api/v1/interviews/
- /api/v1/analytics/
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.django_db

VACANCIES_URL = "/api/v1/vacancies/"
INTERVIEWS_URL = "/api/v1/interviews/"
ANALYTICS_URL = "/api/v1/analytics/"


def _vacancy_payload(**kw):
    return {"title": "Python Developer", "department": "Engineering", **kw}


class TestVacancyAuth:
    def test_anon_cannot_list(self, anon_client):
        assert anon_client.get(VACANCIES_URL).status_code == 401

    def test_anon_cannot_create(self, anon_client):
        assert anon_client.post(VACANCIES_URL, _vacancy_payload(), format="json").status_code == 401

    def test_interviewer_can_list(self, interviewer_client):
        assert interviewer_client.get(VACANCIES_URL).status_code == 200


class TestVacancyCreate:
    def test_create_returns_201(self, recruiter_client):
        assert recruiter_client.post(VACANCIES_URL, _vacancy_payload(), format="json").status_code == 201

    def test_create_is_open_by_default(self, recruiter_client):
        resp = recruiter_client.post(VACANCIES_URL, _vacancy_payload(), format="json")
        assert resp.data["is_open"] is True

    def test_create_missing_title_returns_400(self, recruiter_client):
        assert recruiter_client.post(VACANCIES_URL, {"department": "IT"}, format="json").status_code == 400

    def test_recruiter_id_set_from_token(self, recruiter_client, recruiter_user):
        resp = recruiter_client.post(VACANCIES_URL, _vacancy_payload(), format="json")
        assert resp.data["recruiter_id"] == recruiter_user.id


class TestVacancyList:
    def test_list_empty(self, recruiter_client):
        assert recruiter_client.get(VACANCIES_URL).data == []

    def test_filter_is_open(self, recruiter_client):
        r1 = recruiter_client.post(VACANCIES_URL, _vacancy_payload(title="A"), format="json")
        recruiter_client.post(VACANCIES_URL, _vacancy_payload(title="B"), format="json")
        recruiter_client.post(f"{VACANCIES_URL}{r1.data['id']}/close/", format="json")
        open_resp = recruiter_client.get(VACANCIES_URL + "?is_open=true")
        assert len(open_resp.data) == 1
        assert open_resp.data[0]["title"] == "B"


class TestVacancyDetail:
    def test_get_returns_200(self, recruiter_client):
        vid = recruiter_client.post(VACANCIES_URL, _vacancy_payload(), format="json").data["id"]
        assert recruiter_client.get(f"{VACANCIES_URL}{vid}/").status_code == 200

    def test_get_missing_returns_404(self, recruiter_client):
        assert recruiter_client.get(f"{VACANCIES_URL}9999/").status_code == 404

    def test_delete_returns_204(self, recruiter_client):
        vid = recruiter_client.post(VACANCIES_URL, _vacancy_payload(), format="json").data["id"]
        assert recruiter_client.delete(f"{VACANCIES_URL}{vid}/").status_code == 204


class TestVacancyClose:
    def test_close_sets_is_open_false(self, recruiter_client):
        vid = recruiter_client.post(VACANCIES_URL, _vacancy_payload(), format="json").data["id"]
        resp = recruiter_client.post(f"{VACANCIES_URL}{vid}/close/")
        assert resp.status_code == 200
        assert resp.data["is_open"] is False
        assert resp.data["closed_at"] is not None

    def test_close_idempotent(self, recruiter_client):
        vid = recruiter_client.post(VACANCIES_URL, _vacancy_payload(), format="json").data["id"]
        recruiter_client.post(f"{VACANCIES_URL}{vid}/close/")
        resp = recruiter_client.post(f"{VACANCIES_URL}{vid}/close/")
        assert resp.status_code == 200
        assert resp.data["is_open"] is False

    def test_close_missing_returns_404(self, recruiter_client):
        assert recruiter_client.post(f"{VACANCIES_URL}9999/close/").status_code == 404


@pytest.fixture
def candidate_id(recruiter_client):
    resp = recruiter_client.post(
        "/api/v1/candidates/",
        {"first_name": "A", "last_name": "B", "email": "ab@test.com"},
        format="json",
    )
    return resp.data["id"]


def _interview_payload(candidate_id, interviewer_id, **kw):
    return {
        "candidate_id": candidate_id,
        "interviewer_id": interviewer_id,
        "scheduled_at": "2026-06-01T10:00:00Z",
        **kw,
    }


class TestInterviewAuth:
    def test_anon_cannot_list(self, anon_client):
        assert anon_client.get(INTERVIEWS_URL).status_code == 401

    def test_interviewer_can_list(self, interviewer_client):
        assert interviewer_client.get(INTERVIEWS_URL).status_code == 200


class TestInterviewCreate:
    def test_create_returns_201(self, recruiter_client, candidate_id, interviewer_user):
        resp = recruiter_client.post(INTERVIEWS_URL, _interview_payload(candidate_id, interviewer_user.id), format="json")
        assert resp.status_code == 201

    def test_create_has_null_score(self, recruiter_client, candidate_id, interviewer_user):
        resp = recruiter_client.post(INTERVIEWS_URL, _interview_payload(candidate_id, interviewer_user.id), format="json")
        assert resp.data["score"] is None

    def test_interviewer_cannot_create(self, interviewer_client, candidate_id, interviewer_user):
        resp = interviewer_client.post(INTERVIEWS_URL, _interview_payload(candidate_id, interviewer_user.id), format="json")
        assert resp.status_code == 403


class TestInterviewEvaluate:
    def test_evaluate_sets_score(self, recruiter_client, candidate_id, interviewer_user, interviewer_client):
        iv = recruiter_client.post(INTERVIEWS_URL, _interview_payload(candidate_id, interviewer_user.id), format="json").data
        resp = interviewer_client.patch(f"{INTERVIEWS_URL}{iv['id']}/evaluate/", {"score": 8, "comment": "Great"}, format="json")
        assert resp.status_code == 200
        assert resp.data["score"] == 8

    def test_evaluate_score_out_of_range(self, recruiter_client, candidate_id, interviewer_user, interviewer_client):
        iv = recruiter_client.post(INTERVIEWS_URL, _interview_payload(candidate_id, interviewer_user.id), format="json").data
        resp = interviewer_client.patch(f"{INTERVIEWS_URL}{iv['id']}/evaluate/", {"score": 11}, format="json")
        assert resp.status_code == 400


class TestAnalyticsAuth:
    def test_anon_cannot_access_funnel(self, anon_client):
        assert anon_client.get(f"{ANALYTICS_URL}funnel/").status_code == 401

    def test_anon_cannot_access_time_to_hire(self, anon_client):
        assert anon_client.get(f"{ANALYTICS_URL}time-to-hire/").status_code == 401

    def test_anon_cannot_access_by_status(self, anon_client):
        assert anon_client.get(f"{ANALYTICS_URL}candidates-by-status/").status_code == 401

    def test_interviewer_can_access_funnel(self, interviewer_client):
        assert interviewer_client.get(f"{ANALYTICS_URL}funnel/").status_code == 200

    def test_recruiter_can_access_all(self, recruiter_client):
        for path in ["funnel/", "time-to-hire/", "candidates-by-status/"]:
            assert recruiter_client.get(f"{ANALYTICS_URL}{path}").status_code == 200


class TestAnalyticsEmpty:
    def test_funnel_empty_db(self, recruiter_client):
        resp = recruiter_client.get(f"{ANALYTICS_URL}funnel/")
        assert resp.status_code == 200
        assert isinstance(resp.data, list)
        assert len(resp.data) > 0
        for item in resp.data:
            assert "status" in item
            assert "count" in item

    def test_time_to_hire_empty_db(self, recruiter_client):
        resp = recruiter_client.get(f"{ANALYTICS_URL}time-to-hire/")
        assert resp.status_code == 200
        assert resp.data["hired_count"] == 0
        assert resp.data["avg_seconds"] == 0

    def test_candidates_by_status_empty_db(self, recruiter_client):
        resp = recruiter_client.get(f"{ANALYTICS_URL}candidates-by-status/")
        assert resp.status_code == 200
        assert "NEW" in resp.data
        assert resp.data["NEW"] == 0

    def test_candidates_by_status_with_data(self, recruiter_client):
        recruiter_client.post("/api/v1/candidates/", {"first_name": "A", "last_name": "B", "email": "analytics@test.com"}, format="json")
        resp = recruiter_client.get(f"{ANALYTICS_URL}candidates-by-status/")
        assert resp.data["NEW"] == 1


class TestAnalyticsFunnelStructure:
    def test_funnel_has_conversion_field(self, recruiter_client):
        resp = recruiter_client.get(f"{ANALYTICS_URL}funnel/")
        for item in resp.data:
            assert "conversion_from_prev_pct" in item

    def test_funnel_first_item_has_null_conversion(self, recruiter_client):
        resp = recruiter_client.get(f"{ANALYTICS_URL}funnel/")
        assert resp.data[0]["conversion_from_prev_pct"] is None
