from __future__ import annotations

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.permissions import IsRecruiterOrAdmin, IsRecruiterOrInterviewerReadOnly

from ...dto import InterviewCreateDTO, InterviewEvaluateDTO, InterviewFilterDTO
from ...services.factory import get_interview_service
from .serializers import (
    InterviewCreateSerializer,
    InterviewEvaluateSerializer,
    InterviewReadSerializer,
)


class InterviewListCreateView(APIView):
    permission_classes = [IsRecruiterOrInterviewerReadOnly]

    def get(self, request: Request) -> Response:
        filters = InterviewFilterDTO(
            candidate_id=request.query_params.get("candidate_id") or None,
            interviewer_id=request.query_params.get("interviewer_id") or None,
        )
        items = get_interview_service().list(filters)
        return Response(InterviewReadSerializer(items, many=True).data)

    def post(self, request: Request) -> Response:
        # Лише recruiter/admin створює (RBAC через окремий permission)
        if not IsRecruiterOrAdmin().has_permission(request, self):
            return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

        serializer = InterviewCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        dto = InterviewCreateDTO(
            candidate_id=serializer.validated_data["candidate_id"],
            interviewer_id=serializer.validated_data["interviewer_id"],
            scheduled_at=serializer.validated_data["scheduled_at"],
            recruiter_id=request.user.id,
        )
        created = get_interview_service().schedule(dto)
        return Response(InterviewReadSerializer(created).data, status=status.HTTP_201_CREATED)


class InterviewDetailView(APIView):
    permission_classes = [IsRecruiterOrInterviewerReadOnly]

    def get(self, request: Request, interview_id: int) -> Response:
        return Response(InterviewReadSerializer(get_interview_service().get(interview_id)).data)

    def delete(self, request: Request, interview_id: int) -> Response:
        get_interview_service().delete(interview_id)
        return Response(status=status.HTTP_204_NO_CONTENT)


class InterviewEvaluateView(APIView):
    """PATCH /api/v1/interviews/{id}/evaluate/ — оцінка від інтерв'юера."""
    permission_classes = [IsRecruiterOrInterviewerReadOnly]

    def patch(self, request: Request, interview_id: int) -> Response:
        serializer = InterviewEvaluateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        dto = InterviewEvaluateDTO(**serializer.validated_data)
        updated = get_interview_service().evaluate(interview_id, dto)
        return Response(InterviewReadSerializer(updated).data)
