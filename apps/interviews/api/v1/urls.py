from django.urls import path

from .views import (
    InterviewDetailView,
    InterviewEvaluateView,
    InterviewListCreateView,
)

app_name = "interviews_v1"

urlpatterns = [
    path("", InterviewListCreateView.as_view(), name="list-create"),
    path("<int:interview_id>/", InterviewDetailView.as_view(), name="detail"),
    path(
        "<int:interview_id>/evaluate/",
        InterviewEvaluateView.as_view(),
        name="evaluate",
    ),
]
