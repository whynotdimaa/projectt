"""
RBAC permission classes для DRF.
Користувачі мають ролі: RECRUITER, INTERVIEWER, ADMIN.
"""
from rest_framework import permissions

from .enums import UserRole


class IsRecruiter(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == UserRole.RECRUITER


class IsInterviewer(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == UserRole.INTERVIEWER


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == UserRole.ADMIN


class IsRecruiterOrInterviewer(permissions.BasePermission):
    """Дозвіл для рекрутера або інтерв'юера (напр. читання кандидатів)."""
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.role in {UserRole.RECRUITER, UserRole.INTERVIEWER, UserRole.ADMIN}


class IsRecruiterOrAdmin(permissions.BasePermission):
    """Створення/редагування кандидатів."""
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.role in {UserRole.RECRUITER, UserRole.ADMIN}


class IsRecruiterOrInterviewerReadOnly(permissions.BasePermission):
    """Читання кандидатів дозволено RECRUITER/INTERVIEWER/ADMIN; запис тільки RECRUITER/ADMIN."""
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return request.user.role in {UserRole.RECRUITER, UserRole.INTERVIEWER, UserRole.ADMIN}
        return request.user.role in {UserRole.RECRUITER, UserRole.ADMIN}


class IsRecruiterOrInterviewerWrite(permissions.BasePermission):
    """Повний доступ (читання + запис) для RECRUITER, INTERVIEWER та ADMIN.
    Використовується для /evaluate/ — інтерв'юер повинен мати право PATCH."""
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.role in {UserRole.RECRUITER, UserRole.INTERVIEWER, UserRole.ADMIN}
