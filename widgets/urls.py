from django.urls import path
from . import views

app_name = "widgets"

urlpatterns = [
    path("weather/", views.weather_widget, name="weather"),
]
