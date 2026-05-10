"""Vacancy — відкрита позиція. recruiter — той, хто веде вакансію."""
from django.conf import settings
from django.db import models


class Vacancy(models.Model):
    title = models.CharField(max_length=200)
    department = models.CharField(max_length=100, blank=True, default="")
    description = models.TextField(blank=True, default="")
    recruiter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="vacancies",
    )
    is_open = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "vacancies"
        ordering = ("-created_at",)
        indexes = [models.Index(fields=("is_open",))]

    def __str__(self) -> str:
        return f"{self.title} ({'open' if self.is_open else 'closed'})"
