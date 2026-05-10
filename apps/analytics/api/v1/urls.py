from django.urls import path

from .views import CandidatesByStatusView, FunnelView, TimeToHireView

app_name = "analytics_v1"

urlpatterns = [
    path("funnel/", FunnelView.as_view(), name="funnel"),
    path("time-to-hire/", TimeToHireView.as_view(), name="time-to-hire"),
    path("candidates-by-status/", CandidatesByStatusView.as_view(), name="by-status"),
]
