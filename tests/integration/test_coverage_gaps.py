"""
Coverage-gap tests.
Each test targets specific uncovered lines identified in the coverage report.
Uses real DB (@pytest.mark.django_db) except where noted.
"""
from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.candidates.enums import CandidateStatus
from apps.notifications.dto import NotificationMessage
from apps.notifications.strategies.email_strategy import EmailStrategy
from apps.notifications.strategies.factory import NotificationStrategyFactory
from apps.notifications.strategies.slack_strategy import SlackStrategy
from apps.notifications.strategies.sms_strategy import SMSStrategy
from apps.users.enums import UserRole
from core.exceptions import ConflictError, NotFoundError, ValidationError

User = get_user_model()

pytestmark = pytest.mark.django_db


# ─────────────────────────────────────────────────────────────
#  Model __str__ methods (candidates/models.py lines 37, 62)
# ─────────────────────────────────────────────────────────────

class TestCandidateModelStr:
    def test_candidate_str(self, recruiter_client):
        from apps.candidates.models import Candidate
        c = Candidate.objects.create(
            first_name="Ivan", last_name="Franko", email="ivan_str@test.com"
        )
        assert str(c) == "Ivan Franko <ivan_str@test.com>"

    def test_status_history_str(self, recruiter_client):
        from apps.candidates.models import Candidate, StatusHistory
        c = Candidate.objects.create(
            first_name="Ana", last_name="K", email="ana_str@test.com"
        )
        h = StatusHistory.objects.create(
            candidate=c, from_status="NEW", to_status="SCREENING"
        )
        assert "NEW" in str(h)
        assert "SCREENING" in str(h)


# ─────────────────────────────────────────────────────────────
#  CandidateRepository — uncovered branches (lines 74, 89, 97)
#  These are hit by the integration API tests that already pass.
#  We cover them directly via the repo to ensure 100%.
# ─────────────────────────────────────────────────────────────

class TestCandidateRepositoryBranches:
    def test_update_not_found(self):
        from apps.candidates.dto import CandidateUpdateDTO
        from apps.candidates.repositories.candidate_repository import CandidateRepository
        repo = CandidateRepository()
        with pytest.raises(NotFoundError):
            repo.update(99999, CandidateUpdateDTO(phone="123"))

    def test_update_status_not_found(self):
        from apps.candidates.repositories.candidate_repository import CandidateRepository
        repo = CandidateRepository()
        with pytest.raises(NotFoundError):
            repo.update_status(99999, "SCREENING")

    def test_delete_not_found(self):
        from apps.candidates.repositories.candidate_repository import CandidateRepository
        repo = CandidateRepository()
        with pytest.raises(NotFoundError):
            repo.delete(99999)


# ─────────────────────────────────────────────────────────────
#  VacancyRepository — uncovered branches (lines 37, 62)
# ─────────────────────────────────────────────────────────────

class TestVacancyRepositoryBranches:
    def test_close_not_found(self):
        from apps.vacancies.repositories.vacancy_repository import VacancyRepository
        repo = VacancyRepository()
        with pytest.raises(NotFoundError):
            repo.close(99999)

    def test_delete_not_found(self):
        from apps.vacancies.repositories.vacancy_repository import VacancyRepository
        repo = VacancyRepository()
        with pytest.raises(NotFoundError):
            repo.delete(99999)


# ─────────────────────────────────────────────────────────────
#  InterviewRepository — uncovered branches (lines 35-36, 41, 43,
#  56-63, 66-68)
# ─────────────────────────────────────────────────────────────

class TestInterviewRepositoryBranches:
    def _create_candidate(self):
        from apps.candidates.models import Candidate
        return Candidate.objects.create(
            first_name="A", last_name="B", email=f"iv_{datetime.now().timestamp()}@t.com"
        )

    def _create_interviewer(self):
        return User.objects.create_user(
            email=f"iv_{datetime.now().timestamp()}@t.com",
            password="x", role=UserRole.INTERVIEWER,
            username=f"iv_{datetime.now().timestamp()}@t.com",
        )

    def test_get_by_id_returns_none_for_missing(self):
        from apps.interviews.repositories.interview_repository import InterviewRepository
        repo = InterviewRepository()
        result = repo.get_by_id(99999)
        assert result is None

    def test_list_filter_by_candidate_id(self, recruiter_user, interviewer_user):
        from apps.interviews.dto import InterviewCreateDTO, InterviewFilterDTO
        from apps.interviews.repositories.interview_repository import InterviewRepository
        from apps.candidates.models import Candidate
        c = Candidate.objects.create(first_name="F", last_name="L", email="filter_cand@t.com")
        repo = InterviewRepository()
        repo.add(InterviewCreateDTO(
            candidate_id=c.id, recruiter_id=recruiter_user.id,
            interviewer_id=interviewer_user.id,
            scheduled_at=datetime.now(timezone.utc),
        ))
        items = list(repo.list(InterviewFilterDTO(candidate_id=c.id)))
        assert len(items) >= 1

    def test_list_filter_by_interviewer_id(self, recruiter_user, interviewer_user):
        from apps.interviews.dto import InterviewCreateDTO, InterviewFilterDTO
        from apps.interviews.repositories.interview_repository import InterviewRepository
        from apps.candidates.models import Candidate
        c = Candidate.objects.create(first_name="G", last_name="L", email="filter_iv@t.com")
        repo = InterviewRepository()
        repo.add(InterviewCreateDTO(
            candidate_id=c.id, recruiter_id=recruiter_user.id,
            interviewer_id=interviewer_user.id,
            scheduled_at=datetime.now(timezone.utc),
        ))
        items = list(repo.list(InterviewFilterDTO(interviewer_id=interviewer_user.id)))
        assert len(items) >= 1

    def test_evaluate_not_found(self):
        from apps.interviews.dto import InterviewEvaluateDTO
        from apps.interviews.repositories.interview_repository import InterviewRepository
        repo = InterviewRepository()
        with pytest.raises(NotFoundError):
            repo.evaluate(99999, InterviewEvaluateDTO(score=5, comment="x"))

    def test_evaluate_sets_score(self, recruiter_user, interviewer_user):
        from apps.interviews.dto import InterviewCreateDTO, InterviewEvaluateDTO
        from apps.interviews.repositories.interview_repository import InterviewRepository
        from apps.candidates.models import Candidate
        c = Candidate.objects.create(first_name="H", last_name="L", email="eval_repo@t.com")
        repo = InterviewRepository()
        iv = repo.add(InterviewCreateDTO(
            candidate_id=c.id, recruiter_id=recruiter_user.id,
            interviewer_id=interviewer_user.id,
            scheduled_at=datetime.now(timezone.utc),
        ))
        updated = repo.evaluate(iv.id, InterviewEvaluateDTO(score=7, comment="Good"))
        assert updated.score == 7

    def test_delete_not_found(self):
        from apps.interviews.repositories.interview_repository import InterviewRepository
        repo = InterviewRepository()
        with pytest.raises(NotFoundError):
            repo.delete(99999)

    def test_delete_removes(self, recruiter_user, interviewer_user):
        from apps.interviews.dto import InterviewCreateDTO
        from apps.interviews.repositories.interview_repository import InterviewRepository
        from apps.candidates.models import Candidate
        c = Candidate.objects.create(first_name="I", last_name="L", email="del_repo@t.com")
        repo = InterviewRepository()
        iv = repo.add(InterviewCreateDTO(
            candidate_id=c.id, recruiter_id=recruiter_user.id,
            interviewer_id=interviewer_user.id,
            scheduled_at=datetime.now(timezone.utc),
        ))
        repo.delete(iv.id)
        assert repo.get_by_id(iv.id) is None


# ─────────────────────────────────────────────────────────────
#  InterviewView — uncovered lines (33, 51, 54-55, 63-67)
# ─────────────────────────────────────────────────────────────

INTERVIEWS_URL = "/api/v1/interviews/"


class TestInterviewViewBranches:
    def _create_candidate(self, client):
        resp = client.post(
            "/api/v1/candidates/",
            {"first_name": "A", "last_name": "B", "email": "iv_view@test.com"},
            format="json",
        )
        return resp.data["id"]

    def test_get_single_interview(self, recruiter_client, interviewer_user):
        cid = self._create_candidate(recruiter_client)
        iv = recruiter_client.post(
            INTERVIEWS_URL,
            {"candidate_id": cid, "interviewer_id": interviewer_user.id, "scheduled_at": "2026-07-01T10:00:00Z"},
            format="json",
        ).data
        resp = recruiter_client.get(f"{INTERVIEWS_URL}{iv['id']}/")
        assert resp.status_code == 200

    def test_delete_interview(self, recruiter_client, interviewer_user):
        cid = self._create_candidate(recruiter_client)
        iv = recruiter_client.post(
            INTERVIEWS_URL,
            {"candidate_id": cid, "interviewer_id": interviewer_user.id, "scheduled_at": "2026-07-01T10:00:00Z"},
            format="json",
        ).data
        resp = recruiter_client.delete(f"{INTERVIEWS_URL}{iv['id']}/")
        assert resp.status_code == 204

    def test_evaluate_by_interviewer(self, recruiter_client, interviewer_client, interviewer_user):
        cid = self._create_candidate(recruiter_client)
        iv = recruiter_client.post(
            INTERVIEWS_URL,
            {"candidate_id": cid, "interviewer_id": interviewer_user.id, "scheduled_at": "2026-07-01T10:00:00Z"},
            format="json",
        ).data
        resp = interviewer_client.patch(
            f"{INTERVIEWS_URL}{iv['id']}/evaluate/",
            {"score": 9, "comment": "Excellent"},
            format="json",
        )
        assert resp.status_code == 200
        assert resp.data["score"] == 9


# ─────────────────────────────────────────────────────────────
#  Analytics — stale_candidates (lines 93-94)
# ─────────────────────────────────────────────────────────────

class TestAnalyticsStale:
    def test_stale_candidates_zero_when_fresh(self, recruiter_client):
        # freshly created candidates are NOT stale (updated_at = now)
        recruiter_client.post(
            "/api/v1/candidates/",
            {"first_name": "A", "last_name": "B", "email": "stale1@test.com"},
            format="json",
        )
        from apps.analytics.services.analytics_service import AnalyticsService
        count = AnalyticsService().stale_candidates(days=14)
        assert count == 0

    def test_stale_candidates_excludes_terminal(self):
        from apps.candidates.models import Candidate
        from apps.analytics.services.analytics_service import AnalyticsService
        from django.utils import timezone
        from datetime import timedelta
        # Create a "hired" candidate with old updated_at
        c = Candidate.objects.create(
            first_name="Old", last_name="Hired", email="old_hired@test.com",
            status=CandidateStatus.HIRED,
        )
        # Force updated_at to be old
        Candidate.objects.filter(pk=c.pk).update(
            updated_at=timezone.now() - timedelta(days=30)
        )
        count = AnalyticsService().stale_candidates(days=14)
        assert count == 0  # HIRED is excluded

    def test_stale_candidates_counts_active_old(self):
        from apps.candidates.models import Candidate
        from apps.analytics.services.analytics_service import AnalyticsService
        from django.utils import timezone
        from datetime import timedelta
        c = Candidate.objects.create(
            first_name="Old", last_name="New", email="old_new@test.com",
            status=CandidateStatus.NEW,
        )
        Candidate.objects.filter(pk=c.pk).update(
            updated_at=timezone.now() - timedelta(days=30)
        )
        count = AnalyticsService().stale_candidates(days=14)
        assert count >= 1


# ─────────────────────────────────────────────────────────────
#  Analytics — funnel with history data (lines 45-46, 49-50)
# ─────────────────────────────────────────────────────────────

class TestAnalyticsFunnelWithData:
    def test_funnel_counts_history_transitions(self, recruiter_client):
        # Create candidate and push through funnel to populate history
        cid = recruiter_client.post(
            "/api/v1/candidates/",
            {"first_name": "F", "last_name": "G", "email": "funnel_data@test.com"},
            format="json",
        ).data["id"]
        for status in ["SCREENING", "INTERVIEW"]:
            recruiter_client.patch(
                f"/api/v1/candidates/{cid}/status/",
                {"status": status}, format="json",
            )
        resp = recruiter_client.get("/api/v1/analytics/funnel/")
        assert resp.status_code == 200
        counts = {item["status"]: item["count"] for item in resp.data}
        assert counts["SCREENING"] >= 1
        assert counts["INTERVIEW"] >= 1


# ─────────────────────────────────────────────────────────────
#  User registration view (apps/users/api/v1/views.py lines 11-15
#  and serializers.py lines 15-20)
# ─────────────────────────────────────────────────────────────

class TestUserRegistration:
    REGISTER_URL = "/api/v1/auth/register/"

    def test_register_creates_user(self):
        client = APIClient()
        resp = client.post(
            self.REGISTER_URL,
            {
                "email": "newuser_cov@test.com",
                "password": "strongpass123",
                "first_name": "New",
                "last_name": "User",
                "role": UserRole.RECRUITER,
            },
            format="json",
        )
        assert resp.status_code == 201
        assert "message" in resp.data

    def test_register_missing_email_returns_400(self):
        client = APIClient()
        resp = client.post(
            self.REGISTER_URL,
            {"password": "pass123", "first_name": "A", "last_name": "B"},
            format="json",
        )
        assert resp.status_code == 400


# ─────────────────────────────────────────────────────────────
#  Permissions (lines 12, 17, 22, 28-30, 37)
# ─────────────────────────────────────────────────────────────

class TestPermissions:
    def test_is_recruiter_allows_recruiter(self, recruiter_user):
        from apps.users.permissions import IsRecruiter
        request = MagicMock()
        request.user = recruiter_user
        assert IsRecruiter().has_permission(request, None) is True

    def test_is_recruiter_blocks_interviewer(self, interviewer_user):
        from apps.users.permissions import IsRecruiter
        request = MagicMock()
        request.user = interviewer_user
        assert IsRecruiter().has_permission(request, None) is False

    def test_is_interviewer_allows_interviewer(self, interviewer_user):
        from apps.users.permissions import IsInterviewer
        request = MagicMock()
        request.user = interviewer_user
        assert IsInterviewer().has_permission(request, None) is True

    def test_is_interviewer_blocks_recruiter(self, recruiter_user):
        from apps.users.permissions import IsInterviewer
        request = MagicMock()
        request.user = recruiter_user
        assert IsInterviewer().has_permission(request, None) is False

    def test_is_admin_allows_admin(self, admin_user):
        from apps.users.permissions import IsAdmin
        request = MagicMock()
        request.user = admin_user
        assert IsAdmin().has_permission(request, None) is True

    def test_is_admin_blocks_recruiter(self, recruiter_user):
        from apps.users.permissions import IsAdmin
        request = MagicMock()
        request.user = recruiter_user
        assert IsAdmin().has_permission(request, None) is False

    def test_is_recruiter_or_interviewer_allows_both(self, recruiter_user, interviewer_user):
        from apps.users.permissions import IsRecruiterOrInterviewer
        for user in (recruiter_user, interviewer_user):
            request = MagicMock()
            request.user = user
            assert IsRecruiterOrInterviewer().has_permission(request, None) is True

    def test_is_recruiter_or_interviewer_blocks_anon(self):
        from apps.users.permissions import IsRecruiterOrInterviewer
        from django.contrib.auth.models import AnonymousUser
        request = MagicMock()
        request.user = AnonymousUser()
        assert IsRecruiterOrInterviewer().has_permission(request, None) is False

    def test_is_recruiter_or_admin_blocks_interviewer(self, interviewer_user):
        from apps.users.permissions import IsRecruiterOrAdmin
        request = MagicMock()
        request.user = interviewer_user
        assert IsRecruiterOrAdmin().has_permission(request, None) is False

    def test_is_recruiter_or_admin_blocks_anon(self):
        from apps.users.permissions import IsRecruiterOrAdmin
        from django.contrib.auth.models import AnonymousUser
        request = MagicMock()
        request.user = AnonymousUser()
        assert IsRecruiterOrAdmin().has_permission(request, None) is False


# ─────────────────────────────────────────────────────────────
#  DRF Exception Handler — generic DomainError (line 30)
# ─────────────────────────────────────────────────────────────

class TestExceptionHandler:
    def test_generic_domain_error_returns_400(self):
        from core.drf_exception_handler import custom_exception_handler
        from core.exceptions import DomainError
        exc = DomainError("generic domain problem")
        response = custom_exception_handler(exc, {})
        assert response.status_code == 400
        assert "generic domain problem" in response.data["detail"]

    def test_standard_exception_falls_through(self):
        from core.drf_exception_handler import custom_exception_handler
        # A plain ValueError is not a DomainError — delegated to DRF default handler
        exc = ValueError("something unexpected")
        response = custom_exception_handler(exc, {})
        assert response is None  # DRF default returns None for unknown exceptions


# ─────────────────────────────────────────────────────────────
#  Notification DTO — to_dict (line 14)
# ─────────────────────────────────────────────────────────────

class TestNotificationDTO:
    def test_to_dict(self):
        msg = NotificationMessage(recipient="x@test.com", subject="Subj", body="Body")
        d = msg.to_dict()
        assert d == {"recipient": "x@test.com", "subject": "Subj", "body": "Body"}


# ─────────────────────────────────────────────────────────────
#  Notification strategies — send() (slack line 18, sms line 14)
# ─────────────────────────────────────────────────────────────

class TestNotificationStrategies:
    def test_slack_send_logs(self):
        strategy = SlackStrategy(webhook_url="http://example.com/hook")
        msg = NotificationMessage(recipient="#general", subject="Test", body="Hello Slack")
        # Should not raise
        strategy.send(msg)

    def test_sms_send_logs(self):
        strategy = SMSStrategy()
        msg = NotificationMessage(recipient="+380991234567", subject="Test", body="Hello SMS")
        strategy.send(msg)

    def test_factory_available_channels(self):
        channels = NotificationStrategyFactory.available_channels()
        assert "email" in channels
        assert "slack" in channels
        assert "sms" in channels

    def test_factory_unknown_channel_raises(self):
        with pytest.raises(ValidationError):
            NotificationStrategyFactory.create("carrier_pigeon")


# ─────────────────────────────────────────────────────────────
#  Notification tasks (lines 30-31)
# ─────────────────────────────────────────────────────────────

class TestNotificationTasks:
    def test_send_notification_task_runs(self):
        from apps.notifications.tasks import send_notification_task
        with patch("apps.notifications.tasks.NotificationService") as mock_svc:
            mock_instance = MagicMock()
            mock_svc.for_channels.return_value = mock_instance
            # bind=True tasks expose the underlying function via .run()
            send_notification_task.run(
                channels=["email"],
                message_dict={"recipient": "x@t.com", "subject": "S", "body": "B"},
            )
            mock_instance.send.assert_called_once()

    def test_notify_candidate_status_changed_runs(self):
        from apps.notifications.tasks import notify_candidate_status_changed
        with patch("apps.notifications.tasks.NotificationService") as mock_svc:
            mock_instance = MagicMock()
            mock_svc.for_channels.return_value = mock_instance
            notify_candidate_status_changed.run(
                candidate_email="x@t.com",
                candidate_name="Ivan Franko",
                from_status="NEW",
                to_status="SCREENING",
            )
            mock_instance.send.assert_called_once()


# ─────────────────────────────────────────────────────────────
#  interviews/api/v1/views.py:33 — POST as interviewer → 403
#  (the manual IsRecruiterOrAdmin check inside post())
# ─────────────────────────────────────────────────────────────

class TestInterviewPostForbiddenBranch:
    def test_interviewer_post_hits_manual_403_branch(self, interviewer_client, recruiter_user):
        """
        InterviewListCreateView.post() has an explicit IsRecruiterOrAdmin check
        that returns 403 before reaching the serializer. Hitting this ensures
        line 33 is covered.
        """
        # We need a candidate id — create via DB directly (interviewer cannot POST candidates)
        from apps.candidates.models import Candidate
        c = Candidate.objects.create(
            first_name="X", last_name="Y", email="forbidden_iv_post@test.com"
        )
        resp = interviewer_client.post(
            INTERVIEWS_URL,
            {"candidate_id": c.id, "interviewer_id": 999, "scheduled_at": "2026-07-01T10:00:00Z"},
            format="json",
        )
        assert resp.status_code == 403


# ─────────────────────────────────────────────────────────────
#  users/permissions.py:56 — IsRecruiterOrInterviewerWrite anon
# ─────────────────────────────────────────────────────────────

class TestRecruiterOrInterviewerWritePermission:
    def test_blocks_unauthenticated(self):
        from apps.users.permissions import IsRecruiterOrInterviewerWrite
        from django.contrib.auth.models import AnonymousUser
        request = MagicMock()
        request.user = AnonymousUser()
        assert IsRecruiterOrInterviewerWrite().has_permission(request, None) is False

    def test_allows_interviewer(self, interviewer_user):
        from apps.users.permissions import IsRecruiterOrInterviewerWrite
        request = MagicMock()
        request.user = interviewer_user
        assert IsRecruiterOrInterviewerWrite().has_permission(request, None) is True


# ─────────────────────────────────────────────────────────────
#  vacancies/repositories/vacancy_repository.py:37
#  — list() filter by recruiter_id branch
# ─────────────────────────────────────────────────────────────

class TestVacancyRepoFilterByRecruiter:
    def test_filter_by_recruiter_id(self, recruiter_user):
        from apps.vacancies.dto import VacancyCreateDTO, VacancyFilterDTO
        from apps.vacancies.repositories.vacancy_repository import VacancyRepository
        from apps.users.enums import UserRole
        # Create a second real user so the FK constraint is satisfied
        other_user = User.objects.create_user(
            email="other_recruiter_repo@test.com",
            password="pass",
            role=UserRole.RECRUITER,
            username="other_recruiter_repo@test.com",
        )
        repo = VacancyRepository()
        repo.add(VacancyCreateDTO(title="Dev", recruiter_id=recruiter_user.id))
        repo.add(VacancyCreateDTO(title="QA", recruiter_id=other_user.id))
        items = list(repo.list(VacancyFilterDTO(recruiter_id=recruiter_user.id)))
        assert len(items) == 1
        assert items[0].title == "Dev"

