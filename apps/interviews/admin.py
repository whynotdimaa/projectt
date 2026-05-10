from django.contrib import admin

from .models import Interview


@admin.register(Interview)
class InterviewAdmin(admin.ModelAdmin):
    list_display = ("id", "candidate", "interviewer", "scheduled_at", "score", "evaluated_at")
    list_filter = ("score",)
    search_fields = ("candidate__email",)
