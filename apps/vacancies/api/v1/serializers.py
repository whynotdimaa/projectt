from rest_framework import serializers


class VacancyReadSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField()
    department = serializers.CharField(allow_blank=True)
    description = serializers.CharField(allow_blank=True)
    recruiter_id = serializers.IntegerField()
    is_open = serializers.BooleanField()
    created_at = serializers.DateTimeField(read_only=True)
    closed_at = serializers.DateTimeField(read_only=True, allow_null=True)


class VacancyCreateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=200)
    department = serializers.CharField(max_length=100, required=False, allow_blank=True, default="")
    description = serializers.CharField(required=False, allow_blank=True, default="")
    # recruiter_id заповнимо у view з request.user
