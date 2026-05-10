from django.urls import path

from .views import VacancyCloseView, VacancyDetailView, VacancyListCreateView

app_name = "vacancies_v1"

urlpatterns = [
    path("", VacancyListCreateView.as_view(), name="list-create"),
    path("<int:vacancy_id>/", VacancyDetailView.as_view(), name="detail"),
    path("<int:vacancy_id>/close/", VacancyCloseView.as_view(), name="close"),
]
