from rest_framework import serializers


class InterviewReadSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    candidate_id = serializers.IntegerField()
    recruiter_id = serializers.IntegerField()
    interviewer_id = serializers.IntegerField()
    scheduled_at = serializers.DateTimeField()
    score = serializers.IntegerField(allow_null=True)
    comment = serializers.CharField(allow_blank=True)
    created_at = serializers.DateTimeField(read_only=True)
    evaluated_at = serializers.DateTimeField(read_only=True, allow_null=True)


class InterviewCreateSerializer(serializers.Serializer):
    candidate_id = serializers.IntegerField()
    interviewer_id = serializers.IntegerField()
    scheduled_at = serializers.DateTimeField()


class InterviewEvaluateSerializer(serializers.Serializer):
    score = serializers.IntegerField(min_value=1, max_value=10)
    comment = serializers.CharField(required=False, allow_blank=True, default="")
