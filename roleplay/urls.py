from django.urls import path
from . import views

app_name = "roleplay"

urlpatterns = [
    path("chat/", views.chat, name="chat"),
]
