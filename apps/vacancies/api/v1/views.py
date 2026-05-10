from __future__ import annotations

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.permissions import IsRecruiterOrAdmin, IsRecruiterOrInterviewerReadOnly

from ...dto import VacancyCreateDTO, VacancyFilterDTO
from ...services.factory import get_vacancy_service
from .serializers import VacancyCreateSerializer, VacancyReadSerializer


def _bool_param(val):
    if val is None:
        return None
    return val.lower() in {"1", "true", "yes"}


class VacancyListCreateView(APIView):
    permission_classes = [IsRecruiterOrInterviewerReadOnly]

    def get(self, request: Request) -> Response:
        filters = VacancyFilterDTO(
            is_open=_bool_param(request.query_params.get("is_open")),
            recruiter_id=request.query_params.get("recruiter_id") or None,
        )
        items = get_vacancy_service().list(filters)
        return Response(VacancyReadSerializer(items, many=True).data)

    def post(self, request: Request) -> Response:
        serializer = VacancyCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        dto = VacancyCreateDTO(
            recruiter_id=request.user.id,
            **serializer.validated_data,
        )
        created = get_vacancy_service().create(dto)
        return Response(VacancyReadSerializer(created).data, status=status.HTTP_201_CREATED)


class VacancyDetailView(APIView):
    permission_classes = [IsRecruiterOrInterviewerReadOnly]

    def get(self, request: Request, vacancy_id: int) -> Response:
        return Response(VacancyReadSerializer(get_vacancy_service().get(vacancy_id)).data)

    def delete(self, request: Request, vacancy_id: int) -> Response:
        get_vacancy_service().delete(vacancy_id)
        return Response(status=status.HTTP_204_NO_CONTENT)


class VacancyCloseView(APIView):
    permission_classes = [IsRecruiterOrAdmin]

    def post(self, request: Request, vacancy_id: int) -> Response:
        return Response(VacancyReadSerializer(get_vacancy_service().close(vacancy_id)).data)
