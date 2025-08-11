from django.urls import path
from . import views

app_name = "prompts"

urlpatterns = [
    path("", views.prompt_list, name="list"),
    path("search/", views.search_prompts, name="search"),
    path("create/", views.prompt_create, name="create"),
    path("poem/", views.poem_view, name="poem"),
    path("poem-page/", views.poem_page, name="poem_page"),
    path("<int:pk>/", views.prompt_detail, name="detail"),
    path("<int:pk>/edit/", views.prompt_update, name="update"),
    path("<int:pk>/favorite/", views.toggle_favorite, name="toggle_favorite"),
    path("validate/<str:field_name>/", views.validate_field, name="validate_field"),
]
