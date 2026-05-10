from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.permissions import IsRecruiterOrInterviewerReadOnly

from ...services.analytics_service import AnalyticsService


class FunnelView(APIView):
    permission_classes = [IsRecruiterOrInterviewerReadOnly]

    def get(self, request: Request) -> Response:
        return Response(AnalyticsService().funnel())


class TimeToHireView(APIView):
    permission_classes = [IsRecruiterOrInterviewerReadOnly]

    def get(self, request: Request) -> Response:
        return Response(AnalyticsService().time_to_hire_seconds())


class CandidatesByStatusView(APIView):
    permission_classes = [IsRecruiterOrInterviewerReadOnly]

    def get(self, request: Request) -> Response:
        return Response(AnalyticsService().candidates_by_status())
