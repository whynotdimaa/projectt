"""
Маршрути API v1 для кандидатів.
"""
from django.urls import path

from .views import (
    CandidateDetailView,
    CandidateListCreateView,
    CandidateStatusView,
)

app_name = "candidates_v1"

urlpatterns = [
    path("", CandidateListCreateView.as_view(), name="list-create"),
    path("<int:candidate_id>/", CandidateDetailView.as_view(), name="detail"),
    path(
        "<int:candidate_id>/status/",
        CandidateStatusView.as_view(),
        name="change-status",
    ),
]
