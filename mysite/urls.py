# 프로젝트/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("", include("dashboard.urls")),
    # accounts 앱에서 모든 인증 기능 제공
    path("accounts/", include("accounts.urls")),
    path("admin/", admin.site.urls),
    path("widgets/", include("widgets.urls")),
    path("roleplay/", include("roleplay.urls")),
    path("todo/", include("todo.urls")),
    path("prompts/", include("prompts.urls")),
    path("melon/", include("melon.urls")),
]
