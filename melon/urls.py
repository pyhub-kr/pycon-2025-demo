from django.urls import path
from . import views

app_name = 'melon'

urlpatterns = [
    path('songs/', views.song_list, name='song_list'),
]