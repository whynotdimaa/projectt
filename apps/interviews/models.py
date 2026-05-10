"""
Interview — заплановане інтерв'ю.
score / comment проставляється під час evaluate.
"""
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Interview(models.Model):
    candidate = models.ForeignKey(
        "candidates.Candidate", on_delete=models.CASCADE, related_name="interviews"
    )
    recruiter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="recruiter_interviews",
    )
    interviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="interviewer_interviews",
    )
    scheduled_at = models.DateTimeField()
    score = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
    )
    comment = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    evaluated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "interviews"
        ordering = ("-scheduled_at",)
        indexes = [
            models.Index(fields=("candidate",)),
            models.Index(fields=("scheduled_at",)),
        ]

    def __str__(self) -> str:
        return f"Interview #{self.id} for candidate {self.candidate_id}"
