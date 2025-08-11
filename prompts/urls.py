from django.urls import path
from . import views

app_name = "prompts"

urlpatterns = [
    path("", views.prompt_list, name="list"),
    path("search/", views.search_prompts, name="search"),
    path("<int:pk>/", views.prompt_detail, name="detail"),
    path("<int:pk>/favorite/", views.toggle_favorite, name="toggle_favorite"),
]
