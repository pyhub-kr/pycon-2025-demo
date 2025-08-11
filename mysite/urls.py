# 프로젝트/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("", include("dashboard.urls")),
    # 기본 앱 auth를 추가하는 것 만으로 로그인/로그아웃/암호변경/암호리셋 지원
    path("accounts/", include("django.contrib.auth.urls")),
    path("admin/", admin.site.urls),
    path("widgets/", include("widgets.urls")),
    path("roleplay/", include("roleplay.urls")),
    path("todo/", include("todo.urls")),
    path("prompts/", include("prompts.urls")),
    path("melon/", include("melon.urls")),
]
