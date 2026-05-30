"""
Кастомна модель користувача з полем role (RECRUITER/INTERVIEWER/ADMIN).
Email використовується як username для логіну.
"""
from __future__ import annotations

from django.contrib.auth.models import AbstractUser
from django.db import models

from .enums import UserRole


class User(AbstractUser):
    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length=16,
        choices=UserRole.choices,
        default=UserRole.RECRUITER,
    )
    # phone опціонально
    phone = models.CharField(max_length=32, blank=True, default="")

    # Email як username для автентифікації
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    def save(self, *args, **kwargs):
        # username має бути унікальним, використовуємо email
        self.username = self.email
        super().save(*args, **kwargs)

    class Meta:
        db_table = "users"
        ordering = ("-date_joined",)

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.email} ({self.role})"
