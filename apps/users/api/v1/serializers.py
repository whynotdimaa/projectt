from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        # role виключено: нові користувачі не можуть самостійно обирати роль
        fields = ("id", "email", "first_name", "last_name", "phone", "password")
        read_only_fields = ("id",)

    def create(self, validated_data):
        # Використовуємо create_user() — безпечний спосіб, хешує пароль
        # і уникає mass assignment вразливості
        return User.objects.create_user(**validated_data)
