from django.urls import path
from . import views

app_name = "todo"

urlpatterns = [
    path("", views.todo_list, name="list"),
    path("add/", views.add_todo, name="add"),
    path("<int:pk>/toggle/", views.toggle_todo, name="toggle"),
    path("<int:pk>/edit/", views.edit_todo, name="edit"),
    path("<int:pk>/cancel/", views.cancel_edit, name="cancel"),
    path("<int:pk>/update/", views.update_todo, name="update"),
    path("<int:pk>/delete/", views.delete_todo, name="delete"),
]
