"""
Кореневий URLConf. API роутери підключаються per-app із префіксом /api/v1/.
"""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/candidates/", include("apps.candidates.api.v1.urls")),
    path("api/v1/auth/", include("apps.users.api.v1.urls")),
]
