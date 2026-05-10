"""
Auth endpoints: /api/v1/auth/login/, /api/v1/auth/refresh/
Використовуємо SimpleJWT views напряму (там уже вся логіка токенів).
"""
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import UserRegistrationView

app_name = "auth_v1"

urlpatterns = [
    path("register/", UserRegistrationView.as_view(), name="user_registration"),
    path("login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
