"""
Моделі: Candidate + StatusHistory. ORM-шар.
Бізнес-логіки немає — лише схема. Запис у StatusHistory робить сервіс.
"""
from django.conf import settings
from django.db import models

from .enums import CandidateStatus


class Candidate(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=32, blank=True, default="")
    resume_url = models.URLField(blank=True, default="")
    desired_position = models.CharField(max_length=200, blank=True, default="")

    status = models.CharField(
        max_length=16,
        choices=CandidateStatus.choices,
        default=CandidateStatus.NEW,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "candidates"
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=("status",)),
            models.Index(fields=("created_at",)),
        ]

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name} <{self.email}>"


class StatusHistory(models.Model):
    """Аудит-лог переходів статусів кандидата."""
    candidate = models.ForeignKey(
        Candidate, on_delete=models.CASCADE, related_name="status_history"
    )
    from_status = models.CharField(max_length=16, choices=CandidateStatus.choices)
    to_status = models.CharField(max_length=16, choices=CandidateStatus.choices)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="status_changes",
    )
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "status_history"
        ordering = ("-changed_at",)
        indexes = [models.Index(fields=("candidate", "-changed_at"))]

    def __str__(self) -> str:
        return f"#{self.candidate_id}: {self.from_status} -> {self.to_status}"
