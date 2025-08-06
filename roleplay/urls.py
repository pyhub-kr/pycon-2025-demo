from django.urls import path
from . import views

app_name = "roleplay"

urlpatterns = [
    path("", views.ChatSessionListView.as_view(), name="chatsession_list"),
    path("new/", views.ChatSessionCreateView.as_view(), name="chatsession_new"),
    path("<int:pk>/edit/", views.ChatSessionUpdateView.as_view(), name="chatsession_edit"),
    path("<int:pk>/chat/", views.chat, name="chat"),
]
