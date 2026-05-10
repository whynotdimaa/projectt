"""
DRF views для кандидатів.

Тонкий шар: розпарсити HTTP -> викликати сервіс -> серіалізувати DTO.
Жодних звертань до ORM. Жодної бізнес-логіки. Жодного try/except для
доменних виключень — їх ловить custom_exception_handler.
"""
from __future__ import annotations

from rest_framework import permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.permissions import IsRecruiterOrAdmin, IsRecruiterOrInterviewerReadOnly

from ...dto import (
    CandidateCreateDTO,
    CandidateFilterDTO,
    CandidateUpdateDTO,
)
from ...services.candidate_service import CandidateService
from ...services.factory import get_candidate_service
from .serializers import (
    CandidateCreateSerializer,
    CandidateReadSerializer,
    CandidateStatusSerializer,
    CandidateUpdateSerializer,
)


class _ServiceMixin:
    """Інжектує сервіс. Підмінюється у тестах через monkeypatch."""

    def get_service(self) -> CandidateService:
        return get_candidate_service()


class CandidateListCreateView(_ServiceMixin, APIView):
    """GET /api/v1/candidates/   POST /api/v1/candidates/"""
    permission_classes = [IsRecruiterOrInterviewerReadOnly]

    def get(self, request: Request) -> Response:
        filters = CandidateFilterDTO(
            status=request.query_params.get("status") or None,
            search=request.query_params.get("search") or None,
        )
        items = self.get_service().list(filters)
        data = CandidateReadSerializer(items, many=True).data
        return Response(data)

    def post(self, request: Request) -> Response:
        serializer = CandidateCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        dto = CandidateCreateDTO(**serializer.validated_data)
        created = self.get_service().create(dto)
        return Response(
            CandidateReadSerializer(created).data,
            status=status.HTTP_201_CREATED,
        )


class CandidateDetailView(_ServiceMixin, APIView):
    """GET / PATCH / DELETE /api/v1/candidates/{id}/"""
    permission_classes = [IsRecruiterOrInterviewerReadOnly]

    def get(self, request: Request, candidate_id: int) -> Response:
        item = self.get_service().get(candidate_id)
        return Response(CandidateReadSerializer(item).data)

    def patch(self, request: Request, candidate_id: int) -> Response:
        serializer = CandidateUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        dto = CandidateUpdateDTO(**serializer.validated_data)
        updated = self.get_service().update(candidate_id, dto)
        return Response(CandidateReadSerializer(updated).data)

    def delete(self, request: Request, candidate_id: int) -> Response:
        self.get_service().delete(candidate_id)
        return Response(status=status.HTTP_204_NO_CONTENT)


class CandidateStatusView(_ServiceMixin, APIView):
    """PATCH /api/v1/candidates/{id}/status/"""
    permission_classes = [IsRecruiterOrAdmin]

    def patch(self, request: Request, candidate_id: int) -> Response:
        serializer = CandidateStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        updated = self.get_service().change_status(
            candidate_id, serializer.validated_data["status"]
        )
        return Response(CandidateReadSerializer(updated).data)
