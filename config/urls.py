"""
Кореневий URLConf. API роутери підключаються per-app із префіксом /api/v1/.
"""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/candidates/", include("apps.candidates.api.v1.urls")),
    path("api/v1/auth/", include("apps.users.api.v1.urls")),
    path("api/v1/vacancies/", include("apps.vacancies.api.v1.urls")),
    path("api/v1/interviews/", include("apps.interviews.api.v1.urls")),
]
