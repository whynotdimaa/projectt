"""Ролі користувачів для RBAC."""
from django.db import models


class UserRole(models.TextChoices):
    RECRUITER = "RECRUITER", "Recruiter"
    INTERVIEWER = "INTERVIEWER", "Interviewer"
    ADMIN = "ADMIN", "Admin"
