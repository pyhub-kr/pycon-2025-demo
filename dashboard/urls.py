from django.urls import path, include
from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.dashboard_view, name="home"),
]
