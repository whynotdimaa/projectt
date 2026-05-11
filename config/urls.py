"""
Кореневий URLConf. API роутери підключаються per-app із префіксом /api/v1/.
"""
from django.contrib import admin
from django.urls import include, path

from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/v1/candidates/", include("apps.candidates.api.v1.urls")),
    path("api/v1/auth/", include("apps.users.api.v1.urls")),
    path("api/v1/vacancies/", include("apps.vacancies.api.v1.urls")),
    path("api/v1/interviews/", include("apps.interviews.api.v1.urls")),
    path("api/v1/analytics/", include("apps.analytics.api.v1.urls")),
]
