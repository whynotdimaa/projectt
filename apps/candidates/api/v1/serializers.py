"""
DRF serializers для шару API.

Принципово використовуємо Serializer (а НЕ ModelSerializer), щоб HTTP-шар
не залежав від ORM-моделі. Serializer'и працюють з DTO:
  - Read: DTO -> JSON
  - Write: JSON -> dict (потім в'юшка створює DTO)
"""
from __future__ import annotations

from rest_framework import serializers

from ...enums import CandidateStatus


class CandidateReadSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.EmailField()
    phone = serializers.CharField(allow_blank=True)
    resume_url = serializers.URLField(allow_blank=True)
    desired_position = serializers.CharField(allow_blank=True)
    status = serializers.ChoiceField(choices=CandidateStatus.choices)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


class CandidateCreateSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=32, required=False, allow_blank=True, default="")
    resume_url = serializers.URLField(required=False, allow_blank=True, default="")
    desired_position = serializers.CharField(
        max_length=200, required=False, allow_blank=True, default=""
    )


class CandidateUpdateSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=100, required=False)
    last_name = serializers.CharField(max_length=100, required=False)
    phone = serializers.CharField(max_length=32, required=False, allow_blank=True)
    resume_url = serializers.URLField(required=False, allow_blank=True)
    desired_position = serializers.CharField(max_length=200, required=False, allow_blank=True)


class CandidateStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=CandidateStatus.choices)
