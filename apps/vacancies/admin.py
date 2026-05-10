from django.contrib import admin

from .models import Vacancy


@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "department", "recruiter", "is_open", "created_at", "closed_at")
    list_filter = ("is_open", "department")
    search_fields = ("title", "department")
