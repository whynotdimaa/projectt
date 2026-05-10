"""
Модель Candidate. ORM-шар (Data Access).
Бізнес-логіки тут немає — лише схема + базові інваріанти на рівні БД.
Усі операції створення/оновлення йдуть через repository -> service.
"""
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
