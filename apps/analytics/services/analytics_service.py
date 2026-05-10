"""
AnalyticsService — read-only агрегації по кандидатах і статусній історії.

Use Django ORM aggregates напряму (це read-model). Для аналітики окремий
репозиторій надмірний — сервіс інкапсулює усі запити.
"""
from __future__ import annotations

from datetime import timedelta
from typing import Optional

from django.db.models import Count
from django.utils import timezone

from apps.candidates.enums import CandidateStatus
from apps.candidates.models import Candidate, StatusHistory


class AnalyticsService:
    # Послідовність воронки. HIRED/REJECTED — термінальні.
    FUNNEL_ORDER = (
        CandidateStatus.NEW,
        CandidateStatus.SCREENING,
        CandidateStatus.INTERVIEW,
        CandidateStatus.OFFER,
        CandidateStatus.HIRED,
    )

    def candidates_by_status(self) -> dict[str, int]:
        """Скільки кандидатів зараз у кожному статусі."""
        rows = Candidate.objects.values("status").annotate(n=Count("id"))
        result = {s: 0 for s in CandidateStatus.values}
        for row in rows:
            result[row["status"]] = row["n"]
        return result

    def funnel(self) -> list[dict]:
        """
        Воронка: кількість кандидатів, які КОЛИСЬ досягали кожного статусу,
        + конверсія між сусідніми кроками.
        """
        reached: dict[str, set[int]] = {s: set() for s in self.FUNNEL_ORDER}
        # current
        for c in Candidate.objects.values("id", "status"):
            if c["status"] in reached:
                reached[c["status"]].add(c["id"])
        # будь-який кандидат, що мав цей to_status в історії
        for h in StatusHistory.objects.values("candidate_id", "to_status"):
            if h["to_status"] in reached:
                reached[h["to_status"]].add(h["candidate_id"])

        # також: усі кандидати = NEW (вони стартують з NEW)
        all_candidate_ids = set(Candidate.objects.values_list("id", flat=True))
        reached[CandidateStatus.NEW] |= all_candidate_ids

        result = []
        prev_count: Optional[int] = None
        for status in self.FUNNEL_ORDER:
            count = len(reached[status])
            conversion = (count / prev_count * 100) if prev_count else None
            result.append({
                "status": status,
                "count": count,
                "conversion_from_prev_pct": (
                    round(conversion, 2) if conversion is not None else None
                ),
            })
            prev_count = count if count else prev_count
        return result

    def time_to_hire_seconds(self) -> dict:
        """
        Середній час від створення кандидата до переходу у HIRED.
        Обчислюється у Python — portable для будь-якої БД, об'єм даних малий.
        """
        rows = StatusHistory.objects.filter(
            to_status=CandidateStatus.HIRED,
        ).values("changed_at", "candidate__created_at")

        deltas = [
            (r["changed_at"] - r["candidate__created_at"]).total_seconds()
            for r in rows
        ]
        avg_seconds = sum(deltas) / len(deltas) if deltas else 0
        return {
            "hired_count": len(deltas),
            "avg_seconds": round(avg_seconds, 2),
            "avg_human": str(timedelta(seconds=int(avg_seconds))) if avg_seconds else "0:00:00",
        }

    def stale_candidates(self, days: int = 14) -> int:
        """Скільки кандидатів не оновлювались N днів (потенційно "застрягли")."""
        threshold = timezone.now() - timedelta(days=days)
        return Candidate.objects.filter(
            updated_at__lt=threshold,
        ).exclude(
            status__in=(CandidateStatus.HIRED, CandidateStatus.REJECTED),
        ).count()
